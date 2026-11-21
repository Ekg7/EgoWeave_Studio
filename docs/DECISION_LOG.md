# EgoWeave Studio — Architectural Decision Log

**Project:** EgoWeave Studio  
**Competition:** Samsung PRISM XR Hackathon 2026 — Track 4  
**Date:** November 2026  

---

## Architectural Decision Records (ADRs)

### ADR-001: MobileNetV3Small as Visual Backbone
- **Context:** Need real-time egocentric visual feature extraction on CPU.
- **Decision:** Select MobileNetV3Small (1.0x float, 2.5M params, 10.7 MB).
- **Rationale:** Delivers 9 ms per-frame CPU latency, small memory footprint, and rich ImageNet-1K pretrained semantic features without requiring GPU.

### ADR-002: Quarantine of Synthetic Checkpoints
- **Context:** Three synthetic task heads (`noun_head_best.h5`, `verb_head_best.h5`, `category_head_best.h5`) produced random predictions.
- **Decision:** Move all synthetic heads to `weights/synthetic_quarantine/` and exclude them from production pipeline.
- **Rationale:** Honest, grounded inference with MobileNetV3 + optical flow + Bayesian priors drastically outperforms hallucinated synthetic heads.

### ADR-003: Double-Softmax Removal & Max-Activation Pooling
- **Context:** Keras `MobileNetV3Small(include_top=True)` output is already softmax-normalized. Applying second softmax flattened all probabilities to uniform $0.0010$. Summing synsets biased classes with more synsets (`bottle`, `cooking`).
- **Decision:** Remove the second softmax call. Use `np.max` across valid synsets for each concept.
- **Rationale:** Restores true neural confidence ($0.05$ to $0.80$ when present, $<0.001$ when absent) and eliminates multi-synset bias.

### ADR-004: Evidence Thresholding for Category "other"
- **Context:** An uploaded manufacturing video was falsely classified as `cooking (92%)` with actions `pour bottle`, `pour oil`.
- **Decision:** Require peak probability $\ge 0.010$ and margin $\ge 0.0015$ over runner-up before assigning one of the 15 specific categories. Videos lacking evidence predict `"other"`.
- **Rationale:** Ensures compliance with `supported_classes.json` (which contains `"other"`) and produces truthful predictions for non-domain video content.

### ADR-005: Highlight Budget vs. Minimum 4.0s Rule Resolution
- **Context:** Videos $< 26.67\text{ s}$ cannot satisfy both $\le 15\%$ budget and $\ge 4.0\text{ s}$ segment length.
- **Decision:** Enforce the mandatory $\ge 4.0\text{ s}$ segment constraint, as failing it is a hard rejection in `validate.py`. Update UI to indicate `Min 4.0s Rule Active (Short Clip < 26.7s)`.
- **Rationale:** Guarantees submission validity while clearly explaining the constraint relationship to the user.

### ADR-006: Dedicated Egocentric Action Model vs. 2D ImageNet Proxies
- **Context:** Empirical testing on `P23_01.mp4` demonstrated that 2D ImageNet-1K models cannot recognize egocentric kitchen objects (e.g. onions, paring knives) or physical verbs (`cut`, `stir`, `wash`), reducing action proposals to `other / other`.
- **Decision:** Decouple video processing into:
  1. Optical flow motion valley boundary proposal (fast, lightweight, temporal localization).
  2. Pretrained PySlowFast / TSM dual-head action classification (EPIC-KITCHENS-100 trained) on candidate temporal clips.
  3. Pretrained video-level classifier (Kinetics / CLIP / concept voting) for 16-class activity categorization.
- **Rationale:** Eliminates vocabulary mismatch (ImageNet lacks onions and verbs) and leverages established 70,000-action egocentric training weights without requiring prohibitive full-dataset retraining.

### ADR-007: Selection of TSM (Temporal Shift Module) over SlowFast and C2 BMN
- **Context:** Evaluated official EPIC-KITCHENS-100 implementations: SlowFast (263.9 MB), C2 Action Detection (BMN + SlowFast), and TSM (93.1 MB).
- **Decision:** Select TSM ResNet-50 RGB (`tsm_rgb.ckpt`).
- **Rationale:**
  1. TSM achieves 35.75% Action Top-1 on EPIC-100 with zero extra FLOPs or parameters over 2D ResNet-50, running in < 1.0s on standard CPU hardware.
  2. BMN requires dense multi-gigabyte offline feature caching and takes > 45s on CPU, violating hackathon latency requirements.
  3. Checkpoint matches the 397-unit output head (97 verbs + 300 nouns) mapping 1:1 to Student Kit classes.
