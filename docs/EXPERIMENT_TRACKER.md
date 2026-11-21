# EgoWeave Studio — Experiment Tracker

**Project:** EgoWeave Studio  
**Competition:** Samsung PRISM XR Hackathon 2026 — Track 4  
**Date:** November 2026  

---

## Experiment Registry

| Exp ID | Configuration | Target Metric | Result | Decision |
| :--- | :--- | :--- | :--- | :--- |
| **EXP-00** | Synthetic pilot test fixtures (`test_demo.mp4`, `test_120s.mp4` vs mock JSONs) | Software pipeline throughput & metric formulas | Verified pipeline execution speed (5-8x realtime), JSON formatting, and metrics calculation. Action mAP was 0.0%. | **Pipeline Verified Only.** Confirmed that test files were synthetic mock fixtures (moving white circle on black canvas), not actual ML action recognition. |
| **EXP-01** | Synthetic task heads (`noun_head_best.h5`, `verb_head_best.h5`) | Action mAP | Near zero accuracy; random predictions | **Failed.** Quarantined. |
| **EXP-02** | MobileNetV3 + Farneback optical flow + double softmax | Action Coverage & Category Acc | Severe bias toward `cooking`, `pour bottle`, `pour oil` | **Flawed.** Diagnosed double-softmax flattening. |
| **EXP-03** | MobileNetV3 (single softmax) + max-activation pooling | Category & Noun Grounding | Restored true activation ($0.05-0.80$), eliminated multi-synset bias | **Success.** Adopted into core pipeline. |
| **EXP-04** | Fallback removal + thresholding for `"other"` | Generalization on arbitrary videos | Manufacturing video correctly predicts `label: "other"` and `verb: "other", noun: "other"` | **Success.** Fully eliminates false kitchen hallucinations. |
| **EXP-05** | Minimum 4.0s segment rule priority on short clips | `validate.py` submission compliance | Passes `validate.py` 100% clean on all short and long videos | **Success.** UI updated with informational badge. |
| **EXP-06** | Empirical testing on 91.86s onion-cutting video (`P23_01.mp4`) | Fine-grained `cut onion` recognition | Classified as `cooking (0.70)`; 8 motion segments detected; all 8 actions classified as `other / other` (~0.61 score); zero `cut onion` detected | **Action Recognition Failure.** Proves 2D ImageNet-1K cannot recognize egocentric actions without dedicated egocentric weights. |
