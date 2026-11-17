import numpy as np
from typing import List, Dict, Any, Tuple


def compute_temporal_iou(seg1: List[float], seg2: List[float]) -> float:
    s1, e1 = seg1
    s2, e2 = seg2
    inter = max(0.0, min(e1, e2) - max(s1, s2))
    union = max(e1, e2) - min(s1, s2)
    return inter / union if union > 0 else 0.0


def compute_action_coverage(
    pred_highlights: List[Dict[str, Any]],
    gt_actions: List[Dict[str, Any]],
    duration_sec: float
) -> float:
    """
    Action Coverage (40% Weight):
    Measures the proportion of unique ground-truth (verb, noun) pairs captured
    by the selected highlight segments, with a penalty if highlights exceed 15% budget.
    """
    if not gt_actions:
        return 1.0

    # Extract unique ground-truth action pairs
    gt_pairs = set((a["verb"], a["noun"]) for a in gt_actions)
    captured_pairs = set()

    for ga in gt_actions:
        g_seg = ga["segment"]
        pair = (ga["verb"], ga["noun"])
        for ph in pred_highlights:
            p_seg = ph["segment"]
            # Any non-zero temporal overlap means the action was captured
            if max(0.0, min(g_seg[1], p_seg[1]) - max(g_seg[0], p_seg[0])) > 0.5:
                captured_pairs.add(pair)
                break

    raw_coverage = len(captured_pairs) / len(gt_pairs) if gt_pairs else 1.0

    # Check budget penalty (soft penalty if total highlight length > 15% of duration)
    total_hl_len = sum(h["segment"][1] - h["segment"][0] for h in pred_highlights)
    budget = 0.15 * duration_sec

    if total_hl_len > budget + 0.1 and duration_sec > 0:
        excess = total_hl_len - budget
        penalty = np.exp(-excess / max(1.0, 0.05 * duration_sec))
        raw_coverage *= float(penalty)

    return float(np.clip(raw_coverage, 0.0, 1.0))


def compute_action_map(
    pred_actions: List[Dict[str, Any]],
    gt_actions: List[Dict[str, Any]],
    iou_thresholds: List[float] = None
) -> float:
    """
    Action mAP (25% Weight):
    Mean Average Precision across verb-noun action predictions at temporal IoU thresholds [0.1, 0.2, 0.3, 0.4, 0.5].
    """
    if iou_thresholds is None:
        iou_thresholds = [0.1, 0.2, 0.3, 0.4, 0.5]

    if not gt_actions:
        return 1.0 if not pred_actions else 0.5

    # Group predictions and ground truth by (verb, noun)
    gt_by_class: Dict[Tuple[str, str], List[List[float]]] = {}
    for ga in gt_actions:
        pair = (ga["verb"], ga["noun"])
        gt_by_class.setdefault(pair, []).append(ga["segment"])

    pred_by_class: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for pa in pred_actions:
        pair = (pa["verb"], pa["noun"])
        pred_by_class.setdefault(pair, []).append(pa)

    aps_per_threshold = []

    for tiou in iou_thresholds:
        aps = []
        for pair, g_segs in gt_by_class.items():
            p_items = pred_by_class.get(pair, [])
            if not p_items:
                aps.append(0.0)
                continue

            # Sort predictions descending by score
            p_sorted = sorted(p_items, key=lambda x: x.get("score", 0.0), reverse=True)
            matched = [False] * len(g_segs)
            tp = [0] * len(p_sorted)
            fp = [0] * len(p_sorted)

            for i, p in enumerate(p_sorted):
                p_seg = p["segment"]
                best_iou = 0.0
                best_gt_idx = -1

                for g_idx, g_seg in enumerate(g_segs):
                    iou = compute_temporal_iou(p_seg, g_seg)
                    if iou > best_iou:
                        best_iou = iou
                        best_gt_idx = g_idx

                if best_iou >= tiou and best_gt_idx >= 0 and not matched[best_gt_idx]:
                    tp[i] = 1
                    matched[best_gt_idx] = True
                else:
                    fp[i] = 1

            # Precision-recall curve
            tp_cum = np.cumsum(tp)
            fp_cum = np.cumsum(fp)
            recalls = tp_cum / len(g_segs)
            precisions = tp_cum / (tp_cum + fp_cum)

            # 11-point interpolated AP
            ap = 0.0
            for r_thresh in np.linspace(0.0, 1.0, 11):
                p_above = precisions[recalls >= r_thresh]
                p_max = np.max(p_above) if len(p_above) > 0 else 0.0
                ap += p_max / 11.0
            aps.append(ap)

        aps_per_threshold.append(float(np.mean(aps)) if aps else 0.0)

    return float(np.mean(aps_per_threshold)) if aps_per_threshold else 0.0


def compute_highlight_f1(
    pred_highlights: List[Dict[str, Any]],
    gt_highlights: List[Dict[str, Any]],
    duration_sec: float
) -> float:
    """
    Highlight F1 (25% Weight):
    Frame-level F1 score comparing selected highlights with ground truth.
    Evaluated second-by-second on a 1-second grid.
    """
    if duration_sec <= 0:
        return 0.0

    n_sec = int(np.ceil(duration_sec))
    pred_grid = np.zeros(n_sec, dtype=bool)
    gt_grid = np.zeros(n_sec, dtype=bool)

    for ph in pred_highlights:
        s = max(0, int(np.floor(ph["segment"][0])))
        e = min(n_sec, int(np.ceil(ph["segment"][1])))
        pred_grid[s:e] = True

    for gh in gt_highlights:
        s = max(0, int(np.floor(gh["segment"][0])))
        e = min(n_sec, int(np.ceil(gh["segment"][1])))
        gt_grid[s:e] = True

    intersection = np.sum(pred_grid & gt_grid)
    p_sum = np.sum(pred_grid)
    g_sum = np.sum(gt_grid)

    precision = intersection / p_sum if p_sum > 0 else 0.0
    recall = intersection / g_sum if g_sum > 0 else 0.0

    if precision + recall == 0:
        return 0.0
    f1 = 2 * (precision * recall) / (precision + recall)
    return float(f1)


def compute_label_accuracy(pred_label: Any, gt_label: Any) -> float:
    """
    Label Accuracy (10% Weight):
    Exact match between predicted video-level activity category and ground truth.
    Supports either string labels or dictionary representations {"name": ..., "score": ...}.
    """
    p_name = pred_label.get("name", "") if isinstance(pred_label, dict) else str(pred_label)
    g_name = gt_label.get("name", "") if isinstance(gt_label, dict) else str(gt_label)
    return 1.0 if p_name.strip().lower() == g_name.strip().lower() else 0.0


def compute_composite_score(
    coverage: float,
    map_score: float,
    f1_score: float,
    label_acc: float
) -> float:
    """
    Official 100-Point Composite Formula:
    Score = 0.40 * (Coverage * 100) + 0.25 * (mAP * 100) + 0.25 * (F1 * 100) + 0.10 * (LabelAcc * 100)
    """
    return (
        0.40 * (coverage * 100.0) +
        0.25 * (map_score * 100.0) +
        0.25 * (f1_score * 100.0) +
        0.10 * (label_acc * 100.0)
    )

