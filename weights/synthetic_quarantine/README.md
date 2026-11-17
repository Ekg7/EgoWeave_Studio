# Quarantined Synthetic Checkpoints

> [!CAUTION]
> **QUARANTINE NOTICE (Mission 4B / Mission 5 Audit):**
> The checkpoints and configuration files in this directory:
> - `noun_head_weights.npz` (1,261,185 bytes)
> - `verb_head_weights.npz` (1,128,274 bytes)
> - `category_head_weights.npz` (495,201 bytes)
>
> were trained on **synthetic Gaussian distributions around random/heuristic anchor vectors** rather than human-annotated video frames from EPIC-KITCHENS-100 or FPVSum.
>
> They are strictly **quarantined from production inference** to guarantee scientific validity and prevent ungrounded predictions.
>
> They are preserved here purely for reproducibility, historical provenance, and architectural reference.
> Production inference uses the authentic ImageNet-1K pretrained MobileNetV3-Small backbone (`weights/keras_cache/models/weights_mobilenet_v3_small_224_1.0_float.h5`) combined with dense optical flow and domain-specific Bayesian priors.
