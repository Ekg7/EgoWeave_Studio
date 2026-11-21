# EgoWeave Studio — Development Log

**Project:** EgoWeave Studio  
**Competition:** Samsung PRISM XR Hackathon 2026 — Track 4  
**Date:** November 2026  

---

## Chronological Development Milestones

### Milestone 1: Full-Stack Foundations
- Established React 18.3 + TypeScript + Tailwind CSS frontend.
- Built interactive React Flow temporal interaction graph.
- Implemented FastAPI asynchronous backend with SQLite database and SSE streaming.
- Developed basic FFmpeg highlight video compilation.

### Milestone 2: Independent Audit & Architecture Verification
- Conducted independent audit of model checkpoints.
- Discovered that synthetic task heads (`weights/synthetic_quarantine/`) were trained on uniform synthetic targets, degrading recognition to random chance.
- Isolated synthetic heads into quarantine; standardized on genuine ImageNet-1K pretrained MobileNetV3Small backbone.
- Integrated Bayesian log-odds pair priors and Farneback optical flow motion gating.

### Milestone 3: Official Resource Integration & Root Cleanup
- Ingested updated `TEAM_README.md` and `skiing_03.json` from organizers.
- Eliminated redundant root duplicates (`manifest.csv`, `supported_classes.json`, `TEAM_README.md`, `P02_109.json`, `skiing_03.json`), consolidating all references onto canonical `student_kit/` files.
- Added comprehensive documentation and automated regression testing.

### Milestone 4: Deep AI Bug Resolution & Generalization Fixes
- **Root Cause Identified:** Double softmax in `VisualBackbone.extract_batch_features` flattened all ImageNet class probabilities to uniform $\approx 0.0010$, wiping out visual object signal.
- **Multi-Synset Bias Removed:** Replaced `np.sum` with `np.max` across concept synsets to prevent classes with multiple synsets (e.g. `cooking` with 20 synsets, `bottle` with 5 synsets) from always winning.
- **Eliminated Hallucinated Actions:** Removed `t_ratio` arbitrary fallbacks in `action_recognition.py`. Grounded actions exclusively in genuine visual evidence ($\ge 8\times$ uniform baseline) and physical optical flow.
- **Category Classification Fix:** Removed hardcoded `cooking` fallback for `epic_kitchens_100`. Implemented peak-to-margin thresholding. Videos lacking specific domain features (e.g. manufacturing) correctly classify as `"other"`.
- **UI Short Clip Handling:** Enhanced `HighlightInspector.tsx` to recognize videos $< 26.67\text{s}$ and explain that the $\ge 4.0\text{s}$ segment rule takes precedence per official rules.

### Milestone 5: The Onion-Cutting Recognition Failure & Egocentric Model Audit
- **Test Video:** Tested on authentic 91.86s first-person video `P23_01.mp4` (participant cutting onions).
- **Failure Recorded:** System generated 8 valid temporal segments via optical flow valleys, but labeled all actions as `other / other` (~0.61 confidence). Completely failed to predict `cut onion`.
- **Forensic Diagnosis:**
  - ImageNet-1K has no `onion` class (closest proxy used was `mashed_potato` 935 / `potpie` 964, which yielded $0.00022$ activation).
  - ImageNet-1K has no kitchen chef's knife class (only butcher's `cleaver` 499, which yielded $0.00283$ activation).
  - 2D static CNNs cannot recognize temporal verbs (`cut`, `stir`, `wash`).
  - The 8 action proposals were purely kinetic optical flow energy spikes; the confidence scores (~0.61) were scaled pixel velocities.
- **Action Plan:** Transition from 2D ImageNet heuristic proxies to dedicated egocentric action recognition checkpoints (EPIC-KITCHENS-100 SlowFast / TSM) paired with a small 5-video validation set.
