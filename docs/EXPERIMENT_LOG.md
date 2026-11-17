# EgoWeave Studio — Experiment Log

## Experiment 1: Uniform Sampling vs. Optical Flow Camera-Motion Compensated Sampling
- **Hypothesis:** Raw optical flow on first-person video is dominated by user head rotations. Subtracting median global background motion isolates fine-grained hand and tool interactions.
- **Setup:** Tested on EPIC-KITCHENS sample videos (`P02_109`). Evaluated motion energy peak alignment with ground-truth action start/end boundaries.
- **Results:**
  - Raw flow alignment: $48.2\%$ action boundary recall.
  - Camera-motion compensated flow: $76.8\%$ action boundary recall ($+28.6\%$ improvement).
- **Decision:** Adopted compensated flow in `inference/preprocessing.py`.

---

## Experiment 2: Independent Verb/Noun Top-1 vs. Pair Prior Smoothing
- **Hypothesis:** Predicting verbs and nouns independently creates implausible interactions (e.g. `cut tap`, `open oil`). A Bayesian pair prior $P(v, n) = P(v) \cdot P(n) \cdot \text{Prior}(v, n)$ preserves natural kitchen affordances.
- **Setup:** Evaluated top-5 combinations against EPIC-KITCHENS-100 vocabulary transitions.
- **Results:**
  - Independent predictions: $24\%$ implausible pairs generated.
  - Pair prior smoothing: $0\%$ implausible pairs, Action mAP increased by $+12.4\%$.
- **Decision:** Integrated canonical verb-noun co-occurrence priors in `inference/action_recognition.py`.

---

## Experiment 3: Highlight Duration Budget Calibration (14.2% vs. 15.0%)
- **Hypothesis:** Targeting exactly $15.0\%$ duration risks floating-point boundary rounding penalties during official scoring. Targeting $14.2\% - 14.8\%$ ensures $100\%$ budget compliance while maintaining maximum Action Coverage.
- **Setup:** Tested across all 187 manifest video durations.
- **Results:**
  - $15.0\%$ target: $8.5\%$ of videos triggered soft length penalties due to sub-frame rounding.
  - $14.5\%$ target: $0.0\%$ penalty rate, $100.0\%$ compliance across all test cases.
- **Decision:** Calibrated `target_budget_ratio = 0.145` in `inference/highlight_optimizer.py`.

