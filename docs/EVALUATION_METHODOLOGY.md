# EgoWeave Studio — Evaluation Methodology

**Project:** EgoWeave Studio  
**Competition:** Samsung PRISM XR Hackathon 2026 — Track 4  
**Date:** November 2026  

---

## 1. Official Scoring Protocol

The official Hackathon evaluation formula combines four distinct performance dimensions:

$$\text{Final Score} = 0.40 \times \text{Coverage} + 0.25 \times \text{Action mAP} + 0.25 \times \text{Highlight } F_1 + 0.10 \times \text{Label Accuracy}$$

### 1.1 Action Coverage (Weight: 40%)
- **Definition:** A ground-truth action $A_g = [s_g, e_g]$ is defined as covered if at least $50\%$ of its duration falls within the union of predicted highlight segments:
  $$\text{Coverage}(A_g, H) = \frac{|\bigcup_h ([s_g, e_g] \cap [s_h, e_h])|}{e_g - s_g} \ge 0.50$$
- **Dataset Scope:** Evaluated exclusively on EPIC-KITCHENS-100 videos.
- **Label Independence:** Action coverage measures temporal preservation of meaningful interaction periods; action verb/noun labels do not need to match.

### 1.2 Action Mean Average Precision (mAP) (Weight: 25%)
- Evaluated on temporal Intersection-over-Union ($\text{tIoU} \ge 0.50$).
- A prediction is a true positive if:
  1. $\text{verb}_{\text{pred}} = \text{verb}_{\text{gt}}$
  2. $\text{noun}_{\text{pred}} = \text{noun}_{\text{gt}}$
  3. $\frac{|A_{\text{pred}} \cap A_{\text{gt}}|}{|A_{\text{pred}} \cup A_{\text{gt}}|} \ge 0.50$

### 1.3 Highlight $F_1$ Score (Weight: 25%)
- Computed at 1-second frame resolution across the entire video timeline.
- Let $P_{\text{hl}}$ be binary predicted highlight mask, $G_{\text{hl}}$ be reference highlight mask.
- Precision: $\text{Prec} = \frac{|P \cap G|}{|P|}$, Recall: $\text{Rec} = \frac{|P \cap G|}{|G|}$
- Score: $F_1 = 2 \times \frac{\text{Prec} \times \text{Rec}}{\text{Prec} + \text{Rec}}$

### 1.4 Video Label Accuracy (Weight: 10%)
- Exact match between predicted `label.name` and ground truth activity category across the 16 supported classes.
- Zero credit for invalid class names or names outside `supported_classes.json`.

---

## 2. Benchmark Validation Procedure

Each generated `<video_id>.json` must pass the official validator script:
```bash
python validate.py --file outputs/<video_id>.json -v
```
Or for directory-wide batch verification:
```bash
python validate.py --dir outputs/ -v
```
All 6 mandatory schema keys, value ranges, sorted highlight segments, and vocabulary restrictions are verified automatically.
