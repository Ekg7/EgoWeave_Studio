# EgoWeave Studio — Training & Evaluation Data Audit

**Project:** EgoWeave Studio  
**Competition:** Samsung PRISM XR Hackathon 2026 — Track 4  
**Date:** November 2026  

---

## 1. Inventory of Data Assets

### 1.1 Official Competition Kit (`student_kit/`)
- `supported_classes.json`:
  - 16 Video Activity Labels: `["bike", "bikepolo", "boxing", "cooking", "horse", "jumping", "longboarding", "motor", "parkour", "plane", "rockclimbing", "scuba", "skate", "ski", "surfing", "other"]`
  - 98 Action Verbs: `["take", "put", "wash", "open", "close", "insert", "turn-on", "cut", "turn-off", "pour", "mix", ..., "other"]`
  - 301 Action Nouns: `["pan", "knife", "door", "plate", "cup", "spoon", "fridge", "water", "onion", "tap", ..., "other"]`
- `manifest.csv`:
  - Benchmark manifest containing 28 official evaluation video entries (split between `epic_kitchens_100` and `fpvsum`).
  - Records `video_id`, `duration_sec`, `dataset`, and licensing status.
- Example Ground Truth Outputs:
  - `P02_109.json`: EPIC-KITCHENS-100 kitchen interaction benchmark (duration 512.2s, 31 action segments, 14 highlight segments totaling 73.0s = 14.2% budget).
  - `skiing_03.json`: FPVSum outdoor activity benchmark (duration 258.0s, label `"ski"`, 2 action segments with `verb: "other", noun: "other"`, 3 highlight segments totaling 37.0s = 14.3% budget).
- `TEAM_README.md`:
  - Official rules, benchmark Q&A, scoring weights, and submission requirements.

### 1.2 Model Weights & Pretrained Representations
- `weights/keras_cache/models/weights_mobilenet_v3_small_224_1.0_float.h5`:
  - Genuine Google MobileNetV3Small backbone pretrained on ImageNet-1K (1000 object categories).
  - Size: 10.7 MB.
  - Checksum verified, executes offline without external network calls.
- `weights/imagenet_class_index.json`:
  - Synset and human-readable class names for all 1000 ImageNet categories, used for ontological concept grounding.

### 1.3 Quarantined Synthetic Checkpoints
- `weights/synthetic_quarantine/`:
  - In earlier development iterations, synthetic task heads (`noun_head_best.h5`, `verb_head_best.h5`, `category_head_best.h5`) were created using synthetic uniform pseudo-labels.
  - **Quarantine Action:** An independent audit identified that these synthetic heads degraded visual recognition into random guessing. They have been permanently isolated in `weights/synthetic_quarantine/` and are strictly excluded from the production pipeline.
  - Production inference relies 100% on the genuine ImageNet-1K MobileNetV3 visual backbone, Bayesian pair priors, and physical optical flow dynamics.

---

## 2. Benchmark Manifest Exclusions

Per the official organizer clarifications in `student_kit/TEAM_README.md`:
- `Scuba_KD74Ywuy9ng` (missing raw video asset) is excluded from final scoring.
- `Scuba_Um4kqB8bQBg` (missing raw video asset) is excluded from final scoring.
- Final leaderboard ranking is computed across the remaining 26 available videos.
