# EgoWeave Studio — Experiment Tracker

**Project:** EgoWeave Studio  
**Competition:** Samsung PRISM XR Hackathon 2026 — Track 4  
**Date:** November 2026  

---

## Experiment Registry

| Exp ID | Configuration | Target Metric | Result | Decision |
| :--- | :--- | :--- | :--- | :--- |
| **EXP-01** | Synthetic task heads (`noun_head_best.h5`, `verb_head_best.h5`) | Action mAP | Near zero accuracy; random predictions | **Failed.** Quarantined. |
| **EXP-02** | MobileNetV3 + Farneback optical flow + double softmax | Action Coverage & Category Acc | Severe bias toward `cooking`, `pour bottle`, `pour oil` | **Flawed.** Diagnosed double-softmax flattening. |
| **EXP-03** | MobileNetV3 (single softmax) + max-activation pooling | Category & Noun Grounding | Restored true activation ($0.05-0.80$), eliminated multi-synset bias | **Success.** Adopted into core pipeline. |
| **EXP-04** | Fallback removal + thresholding for `"other"` | Generalization on arbitrary videos | Manufacturing video correctly predicts `label: "other"` and `verb: "other", noun: "other"` | **Success.** Fully eliminates false kitchen hallucinations. |
| **EXP-05** | Minimum 4.0s segment rule priority on short clips | `validate.py` submission compliance | Passes `validate.py` 100% clean on all short and long videos | **Success.** UI updated with informational badge. |
