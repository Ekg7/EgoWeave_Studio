# EgoWeave Studio — Known Issues & Technical Constraints

**Project:** EgoWeave Studio  
**Competition:** Samsung PRISM XR Hackathon 2026 — Track 4  
**Date:** November 2026  

---

## 1. Ultra-Short Video Highlight Budget (< 26.67 seconds)

- **Issue:** The competition specification stipulates both:
  1. Total highlight duration $\le 15.0\%$ of video duration.
  2. At least one highlight segment must be $\ge 4.0\text{ s}$.
- **Conflict:** For videos shorter than $26.67\text{ s}$ ($0.15 \times 26.67 = 4.0\text{ s}$), any highlight segment of $\ge 4.0\text{ s}$ will mathematically exceed $15.0\%$ of the video duration.
- **Handling:**
  - `validate.py` treats a missing $\ge 4.0\text{ s}$ segment as a **FATAL ERROR** (rejection), while treating exceeding $15\%$ on short clips as an advisory **WARNING**.
  - EgoWeave's `HighlightOptimizer` prioritizes the mandatory $\ge 4.0\text{ s}$ rule to ensure submission validity.
  - The frontend UI `HighlightInspector` detects `durationSec < 26.67` and displays `Min 4.0s Rule Active (Short Clip < 26.7s)` in amber rather than a false-positive red failure badge.

---

## 2. Missing Benchmark Video Assets

- **Issue:** In the official `student_kit/manifest.csv`, two entries from the YouTube-sourced FPVSum dataset cannot be fetched or processed:
  - `Scuba_KD74Ywuy9ng`
  - `Scuba_Um4kqB8bQBg`
- **Official Clarification:** As confirmed in `student_kit/TEAM_README.md`, both videos are excluded from final evaluation and scoring.

---

## 3. High-Motion Egocentric Blur on MobileNetV3

- **Issue:** Severe camera rotation (e.g. abrupt head turns) can induce significant optical blur, temporarily depressing visual classification probabilities.
- **Mitigation:**
  - Optical flow novelty detection flags sudden camera rotational spikes.
  - Action proposals snap to optical flow valleys (hand pauses), avoiding blurred transition frames.
  - Multi-scale temporal windowing ($2.0\text{s}$, $4.0\text{s}$, $6.0\text{s}$) integrates visual evidence over multiple frames rather than relying on a single blurred frame.

---

## 4. 2D ImageNet Semantic Gap for Fine-Grained Egocentric Actions

- **Issue:** Static 2D ImageNet-1K pretrained backbones lack vocabulary for common egocentric objects (e.g. `onion`, kitchen knives, cutting boards) and possess zero temporal awareness of verbs (`cut`, `pour`, `mix`, `wash`, `take`, `put`).
- **Consequence:** In genuine cooking footage (such as `P23_01.mp4`), optical flow successfully isolates 8 motion intervals, but the visual model fails to ground `onion` ($p = 0.00022$) or `knife` ($p = 0.00283$), resulting in fallback `other / other` action predictions.
- **Permanent Fix:** Requires replacing frame-by-frame 2D synset proxies with an egocentric video model (SlowFast / TSM) pretrained on EPIC-KITCHENS-100 verb-noun classes.

---

## 5. Synthetic Test Fixtures in `tests/sample_data/`

- **Issue:** Files `test_demo.mp4` and `test_120s.mp4` in `tests/sample_data/` are synthetic geometric videos (black canvases with moving white dots/circles). Their companion files `test_demo.json` and `test_120s.json` are handcrafted unit-test fixtures containing arbitrary mock labels (`open fridge`, `cut onion`), not AI model outputs or genuine human annotations.
- **Mitigation & Clean Boundary:**
  - These files are preserved strictly as **software engineering pipeline fixtures** for testing throughput, video decoding, and schema compliance in `pytest`.
  - They are strictly excluded from representing ML benchmark metrics. All future action recognition evaluations will be measured against authentic annotated datasets.
