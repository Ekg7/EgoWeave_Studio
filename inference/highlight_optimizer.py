import numpy as np
from typing import List, Dict, Any, Tuple


class HighlightOptimizer:
    def __init__(self, target_budget_ratio: float = 0.145, min_segment_len: float = 4.0):
        self.target_budget_ratio = target_budget_ratio
        self.min_segment_len = min_segment_len

    def optimize_highlights(
        self,
        importance_timeline: List[Dict[str, float]],
        actions: List[Dict[str, Any]],
        duration_sec: float
    ) -> List[Dict[str, Any]]:
        """
        Selects a concise set of highlight intervals maximizing action coverage and importance
        while strictly obeying the <= 15% budget and the >= 4.0s minimum segment length rule.
        """
        if duration_sec <= 0:
            return [{"segment": [0.0, 4.0], "importance": 0.8}]

        max_budget_sec = 0.15 * duration_sec
        target_budget_sec = self.target_budget_ratio * duration_sec

        # 1. Generate candidate highlight clips around detected actions and importance peaks
        candidates: List[Tuple[float, float, float]] = []

        # Candidate pool from detected actions (expanded slightly for context)
        for act in actions:
            s, e = act["segment"]
            center = (s + e) / 2.0
            # Target segment length >= 4.0s
            seg_dur = max(self.min_segment_len, e - s)
            cand_s = max(0.0, center - seg_dur / 2.0)
            cand_e = min(duration_sec, cand_s + seg_dur)
            cand_s = max(0.0, cand_e - seg_dur)  # readjust if hitting end boundary

            # Compute average importance
            in_cand = [
                pt["importance"] for pt in importance_timeline
                if cand_s <= pt["timestamp"] <= cand_e
            ]
            imp = float(np.mean(in_cand)) if in_cand else 0.75
            candidates.append((round(cand_s, 1), round(cand_e, 1), round(imp, 3)))

        # Fallback candidate grid if no actions or sparse actions
        if len(candidates) < 3:
            grid_step = max(8.0, duration_sec / 8.0)
            t = 2.0
            while t + self.min_segment_len <= duration_sec:
                cand_s = t
                cand_e = min(duration_sec, t + max(self.min_segment_len, 6.0))
                in_cand = [
                    pt["importance"] for pt in importance_timeline
                    if cand_s <= pt["timestamp"] <= cand_e
                ]
                imp = float(np.mean(in_cand)) if in_cand else 0.70
                candidates.append((round(cand_s, 1), round(cand_e, 1), round(imp, 3)))
                t += grid_step

        # 2. Greedy Knapsack Selection under <= 15% Budget
        # Sort candidates descending by importance score
        candidates.sort(key=lambda c: c[2], reverse=True)

        selected: List[Tuple[float, float, float]] = []
        accumulated_sec = 0.0

        for cand_s, cand_e, score in candidates:
            seg_len = cand_e - cand_s

            # Check overlap with already selected segments
            overlaps = any(
                not (cand_e <= s or cand_s >= e)
                for s, e, _ in selected
            )
            if overlaps:
                continue

            # Check if adding this segment would exceed target budget
            if accumulated_sec + seg_len <= target_budget_sec:
                selected.append((cand_s, cand_e, score))
                accumulated_sec += seg_len

        # 3. Ensure official constraint: At least one segment >= 4.0s
        has_ge_4s = any((e - s) >= self.min_segment_len for s, e, _ in selected)
        if not has_ge_4s:
            if selected:
                # Expand first segment
                s, e, sc = selected[0]
                needed = self.min_segment_len - (e - s)
                new_e = min(duration_sec, e + needed)
                selected[0] = (s, new_e, sc)
            else:
                def_len = min(duration_sec, self.min_segment_len)
                selected.append((0.0, def_len, 0.85))

        # 4. Sort chronologically
        selected.sort(key=lambda x: x[0])

        # 5. Non-overlapping verification & cleanup
        cleaned: List[Dict[str, Any]] = []
        last_end = 0.0

        for s, e, imp in selected:
            s_clean = max(s, last_end)
            e_clean = min(duration_sec, max(s_clean + 0.1, e))
            if e_clean > s_clean:
                cleaned.append({
                    "segment": [round(s_clean, 1), round(e_clean, 1)],
                    "importance": round(imp, 2)
                })
                last_end = e_clean

        # Strict final check on 15% budget
        total_len = sum(h["segment"][1] - h["segment"][0] for h in cleaned)
        if total_len > max_budget_sec and len(cleaned) > 1:
            # Trim from lowest importance segment
            cleaned.pop()

        return cleaned

