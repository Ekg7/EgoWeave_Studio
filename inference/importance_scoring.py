import numpy as np
from typing import List, Dict, Any


class ImportanceScorer:
    def __init__(self, w_motion: float = 0.35, w_action: float = 0.45, w_novelty: float = 0.20):
        self.w_motion = w_motion
        self.w_action = w_action
        self.w_novelty = w_novelty

    def compute_frame_importance(
        self,
        motion_profile: List[Dict[str, float]],
        actions: List[Dict[str, Any]],
        duration_sec: float,
        video_features: Dict[str, Any] = None
    ) -> List[Dict[str, float]]:
        """
        Calculates second-by-second temporal importance scores combining motion energy,
        predicted action coverage, and deep visual novelty.
        """
        if duration_sec <= 0:
            return []

        num_seconds = int(np.ceil(duration_sec))
        importance_timeline = []

        # Map actions to temporal density array
        action_density = np.zeros(num_seconds)
        for act in actions:
            s, e = act["segment"]
            s_idx = max(0, int(np.floor(s)))
            e_idx = min(num_seconds, int(np.ceil(e)))
            action_density[s_idx:e_idx] += act.get("score", 0.8)

        if np.max(action_density) > 0:
            action_density /= np.max(action_density)

        # Interpolate motion and novelty onto 1-second grid
        if motion_profile:
            m_times = np.array([m["timestamp"] for m in motion_profile])
            m_vals = np.array([m["motion_energy"] for m in motion_profile])
            n_vals = np.array([m["novelty"] for m in motion_profile])
        else:
            m_times = np.array([0.0, duration_sec])
            m_vals = np.array([0.2, 0.2])
            n_vals = np.array([0.2, 0.2])

        # Deep semantic novelty from visual features
        has_semantic = (
            video_features is not None
            and "probs" in video_features
            and len(video_features["probs"]) > 1
        )
        if has_semantic:
            probs = video_features["probs"]
            ts_f = video_features["timestamps"]
            sem_diffs = [0.1]
            for i in range(1, len(probs)):
                # L1 variation between semantic scene probability vectors
                diff = float(np.sum(np.abs(probs[i] - probs[i - 1]))) / 2.0
                sem_diffs.append(diff)
            sem_diffs = np.array(sem_diffs)
            if np.max(sem_diffs) > 0:
                sem_diffs /= np.max(sem_diffs)

        for sec in range(num_seconds):
            t = float(sec)
            m_val = float(np.interp(t, m_times, m_vals))
            n_val = float(np.interp(t, m_times, n_vals))
            a_val = float(action_density[sec])

            if has_semantic:
                sem_val = float(np.interp(t, ts_f, sem_diffs))
                n_val = 0.5 * n_val + 0.5 * sem_val

            score = self.w_motion * m_val + self.w_action * a_val + self.w_novelty * n_val
            importance_timeline.append({
                "timestamp": t,
                "importance": float(np.clip(score, 0.05, 0.99))
            })

        return importance_timeline

