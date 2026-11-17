# EgoWeave Studio — Mission 5 Genuine Pilot Evaluation Report
**Samsung PRISM XR Hackathon 2026 — Track 4**  
*Document Version: 1.0*  
*Audit Date: November 17, 2026*

---

## 1. Executive Summary

In Phase 3 of Mission 5, we executed an independent, unmanipulated pilot evaluation comparing EgoWeave's production inference predictions against ground-truth annotations across available video test cases (`test_120s.mp4` and `test_demo.mp4`).

> [!IMPORTANT]
> **Zero Data Leakage & Zero Self-Comparison:**
> All prior synthetic scores (e.g. 76.70/100 placeholder constants, 100/100 self-comparisons) have been discarded.
> Predictions were generated dynamically from raw video MP4 files by `EgoWeavePipeline.process_video()`. Metrics were calculated strictly using `inference/metrics.py` following the Samsung PRISM Track 4 formula:
> $$\text{Score} = 40\% \cdot \text{Action Coverage} + 25\% \cdot \text{Action mAP} + 25\% \cdot \text{Highlight F1} + 10\% \cdot \text{Label Accuracy}$$

---

## 2. Empirical Pilot Benchmark Results

```text
========================================================================
PILOT EVALUATION SUMMARY (Mission 5 Baseline)
========================================================================
Video ID        Duration   Inference  Coverage   mAP      HL F1    Score   
------------------------------------------------------------------------
test_120s       120.0s     28.60s     40.0%      0.0%     0.0%     26.00 / 100
test_demo        15.0s      5.74s     10.4%      0.0%     100.0%   39.17 / 100
------------------------------------------------------------------------
MEAN            —          —          25.2%      0.0%     50.0%    32.59 / 100
========================================================================
```

### Detailed Video Analysis:

#### 1. `test_demo.mp4` (EPIC-KITCHENS-100 Domain, 15.0s)
* **Execution Time:** 5.74 seconds (**2.61x real-time processing speed** on CPU).
* **Label Accuracy:** **100.0%** (predicted `"cooking"` with confidence 0.71; ground-truth: `"cooking"`).
* **Highlight F1:** **100.0%** (The highlight optimizer selected segment `[0.0, 4.0]`, perfectly capturing the ground-truth highlight interval with full temporal precision).
* **Action Coverage:** **10.4%** (Identified opening hand-object interaction).
* **Action mAP:** **0.0%** (The baseline segment merger merged overlapping detections into a single wide interval `[0.0, 14.5]`, which exceeded the fine-grained ground-truth action bounds `[0.0, 2.5]`, reducing tIoU below the 0.1 threshold).
* **Total Composite Score:** **39.17 / 100.0**.

#### 2. `test_120s.mp4` (FPVSum Domain, 120.0s)
* **Execution Time:** 28.60 seconds (**4.20x real-time processing speed** on CPU).
* **Label Accuracy:** **100.0%** (predicted `"cooking"` with confidence 0.92; ground-truth: `"cooking"`).
* **Action Coverage:** **40.0%** (Selected highlights overlapped with 40% of ground-truth action time).
* **Highlight F1:** **0.0%** (Selected high-motion highlights did not match consensus frame labels).
* **Action mAP:** **0.0%** (By competition contract, FPVSum videos have 0 actions evaluated).
* **Total Composite Score:** **26.00 / 100.0**.

---

## 3. Targeted Diagnosis of Baseline Weaknesses

The pilot benchmark reveals the exact algorithmic bottlenecks:
1. **Over-Aggressive Segment Merging:** `_merge_adjacent_actions` was merging all detections of the same category across up to 35 seconds. This collapsed fine-grained, repetitive actions (e.g. cutting 3 slices, picking up tools) into one giant segment, ruining temporal IoU (Action mAP = 0.0%).
2. **Single-Action Window Bottleneck:** `detect_actions` kept only the single top-scoring action per sliding window, ignoring co-occurring or rapid sequential actions.
3. **Motion-Valley Boundary Snapping:** The system lacked boundary snapping based on optical flow minima (when a hand finishes one interaction and moves to the next).
