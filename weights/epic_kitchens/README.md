# EPIC-KITCHENS-100 Pretrained Models Directory

This directory stores verified egocentric action recognition checkpoints evaluated on the EPIC-KITCHENS-100 benchmark.

## Download Official TSM Checkpoint (93.1 MB)

To download the official EPIC-KITCHENS-100 TSM ResNet-50 RGB checkpoint:

```powershell
python tools/download_tsm_checkpoint.py
```

This downloads `tsm_rgb.ckpt` directly from the official EPIC-KITCHENS C1 Action Recognition repository.

## Model Specifications:
- **Architecture:** ResNet-50 with Temporal Shift Module (TSM)
- **Modality:** RGB (8 uniform segments per interval, 224x224 input)
- **Output Classes:** 397 logits (97 EPIC-100 verbs + 300 EPIC-100 nouns)
- **Top-1 Action Accuracy (Val):** 35.75%
- **CPU Inference Speed:** ~3.5 - 4.5 seconds per proposal on standard CPU
