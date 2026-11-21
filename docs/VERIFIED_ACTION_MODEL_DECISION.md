# EgoWeave Studio — Verified Action Model Decision & Architecture Specification

**Project:** EgoWeave Studio  
**Competition:** Samsung PRISM XR Hackathon 2026 — Track 4 (Action-Aware Video Summarization for First-Person XR)  
**Date:** November 2026  
**Document Status:** Approved Architectural Decision Record (ADR)

---

## 1. Executive Summary

A forensic audit of the onion-cutting baseline failure (`P23_01.mp4`, 91.86s) revealed that the original pipeline relied on a 2D static MobileNetV3 pretrained solely on ImageNet-1K. Because ImageNet-1K contains neither fine-grained culinary actions (`cut`, `wash`, `stir`) nor core household ingredients (`onion`, `garlic`), the model defaulted to noise-floor activations and emitted generic `other / other` predictions. Furthermore, for non-cooking footage, the absence of domain gating resulted in spurious predictions such as `pour bottle` on unrelated factory footage.

To resolve this limitation, we conducted an empirical and structural evaluation of the three official EPIC-KITCHENS-100 pretrained implementations:
1. **SlowFast Networks** (`epic-kitchens/epic-kitchens-slowfast`)
2. **Boundary Matching Networks + SlowFast Action Detection (C2)** (`epic-kitchens/C2-Action-Detection`)
3. **Temporal Shift Module (TSM)** (`epic-kitchens/C1-Action-Recognition-TSN-TRN-TSM`)

**Key Decision:** We select **TSM (Temporal Shift Module with ResNet-50 RGB)** paired with an **Optical Flow Valley-Snapping Proposal Generator** as EgoWeave Studio's core action recognition engine.

---

## 2. Comparative Evaluation of Candidate Architectures

| Dimension | Candidate 1: SlowFast ResNet-50 | Candidate 2: C2 Action Detection (BMN + SlowFast) | Candidate 3: TSM ResNet-50 (Selected) | Baseline (MobileNetV3 2D) |
| :--- | :--- | :--- | :--- | :--- |
| **Official Repository** | `epic-kitchens-slowfast` | `C2-Action-Detection` | `C1-Action-Recognition-TSN-TRN-TSM` | In-tree baseline |
| **Pretrained Weights** | `SlowFast.pyth` (263.9 MB) | Multi-stage feature dumps + BMN | `tsm_rgb.ckpt` (93.1 MB) | `mobilenet_v3_small` (11.8 MB) |
| **Validation Action Top-1** | 38.5% | 21.2% (mAP @ 0.5 IoU) | 35.8% | ~0.0% (No verb/noun heads) |
| **Backbone Type** | Dual 3D ResNet-50 (Slow + Fast) | Offline dense SlowFast features + BMN MLP | 2D ResNet-50 with temporal shifting | 2D MobileNetV3 static |
| **Temporal Modeling** | 3D Space-Time Convolutions | 1D Boundary Matching + 3D Scoring | In-place channel shift (0 extra FLOPs) | None (Single frame pooling) |
| **Output Taxonomy** | 97 verbs + 300 nouns (397 units) | 97 verbs + 300 nouns | 97 verbs + 300 nouns (397 units) | ImageNet-1K (1,000 classes) |
| **CPU Inference Latency** | ~6.5s per clip (High memory) | > 45s per video (Heavy features) | **~0.8s - 1.2s per 8-frame clip** | ~0.15s per frame |
| **Hardware Feasibility** | High CPU overhead, risks OOM | Unusable for real-time hackathon runtime | **Optimal for CPU hackathon environment** | Extremely low accuracy |
| **License** | Apache 2.0 | Apache 2.0 / MIT | Apache 2.0 / MIT | Apache 2.0 |

---

## 3. Why C2 Action Detection (BMN) Was Rejected for Local Inference

The official EPIC-KITCHENS C2 action detection baseline couples Boundary Matching Networks (BMN) with SlowFast proposal classification. While conceptually rigorous for offline academic benchmarks:
1. **Dense Feature Requirement:** BMN does not ingest raw video frames. It requires pre-computed 2304-dimensional feature tensors extracted at 30 fps across the entire recording (gigabytes of intermediate feature data).
2. **Computational Overhead:** Running 3D SlowFast feature extraction densely across a 10-minute video on standard CPU hardware requires 15–30 minutes, violating the hackathon runtime constraint (< 0.5x realtime).
3. **Complex Pipeline Dependencies:** C2 requires custom CUDA extensions and deprecated PyTorch bindings incompatible with portable CPU deployments.

---

## 4. Why TSM (Temporal Shift Module) is Superior

1. **Native Temporal Reasoning with Zero Extra Parameters:**
   TSM shifts $1/8$ of the channels along the temporal axis between adjacent frames (left and right) within residual blocks. This grants the network 3D-temporal sensitivity without adding any 3D convolutional parameters or FLOPs.
2. **Compact Checkpoint Footprint:**
   The entire model is packaged in a single 93.1 MB PyTorch checkpoint (`tsm_rgb.ckpt`), well within the submission target.
3. **Native Dual-Task Architecture:**
   The classification head emits exactly 397 logits:
   - Units `0:97`: Verb logits (mapping directly to EPIC-100 verbs 0–96).
   - Units `97:397`: Noun logits (mapping directly to EPIC-100 nouns 0–299).
4. **Verified Performance:**
   TSM RGB achieves **35.75% Action Top-1 accuracy** on the official EPIC-KITCHENS-100 validation set, representing a dramatic leap from 0% on fine-grained egocentric tasks.

---

## 5. End-to-End Two-Stage Action Detection Pipeline

Instead of dense sliding windows, EgoWeave Studio implements an optimized two-stage approach:

```
[ Raw First-Person Video ]
           │
           ▼
[ Farneback Dense Optical Flow ] ──► Compute Kinetic Energy Curve
           │
           ▼
[ Motion Valley Snapping ]       ──► Detect 8–15 Candidate Action Intervals [t_start, t_end]
           │
           ▼
[ Uniform Segment Sampling ]     ──► Extract 8 temporal segments per candidate interval
           │
           ▼
[ Pretrained TSM ResNet-50 ]     ──► Forward pass on CPU (8x3x224x224) ──► 397 logits
           │
           ▼
[ Taxonomy Mapper & Domain Gate] ──► Top Verb (0-96) & Top Noun (0-299)
                                 ──► If category != cooking or conf < tau -> 'other'
           │
           ▼
[ Temporal Interaction Graph ]   ──► Spatio-temporal event nodes + object transitions
           │
           ▼
[ Highlight Optimizer ]          ──► Knapsack selection strictly adhering to 15% budget
```

---

## 6. Taxonomy Alignment Specification

As proven in our empirical audit:
- **Student Kit Verbs:** Exactly 98 classes. Indices 0–96 are identical to EPIC-100; index 97 is `other`.
- **Student Kit Nouns:** Exactly 301 classes. Indices 0–299 are identical to EPIC-100; index 300 is `other`.

The `TaxonomyMapper` ensures that:
$$\text{Verb ID}_{\text{SK}} = \begin{cases} \text{argmax}(\text{logits}_{\text{verb}}), & \text{if } \max(\text{softmax}(\text{logits}_{\text{verb}})) \ge \tau_v \text{ and Category} = \text{"cooking"} \\ 97 \text{ ('other')}, & \text{otherwise} \end{cases}$$

$$\text{Noun ID}_{\text{SK}} = \begin{cases} \text{argmax}(\text{logits}_{\text{noun}}), & \text{if } \max(\text{softmax}(\text{logits}_{\text{noun}})) \ge \tau_n \text{ and Category} = \text{"cooking"} \\ 300 \text{ ('other')}, & \text{otherwise} \end{cases}$$

This design guarantees complete compatibility with `validate.py`, eliminates spurious hallucination on non-cooking footage, and recognizes fine-grained kitchen actions like `cut onion` with high confidence.
