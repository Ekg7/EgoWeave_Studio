# EgoWeave Studio — Model Selection and Justification

**Project:** EgoWeave Studio  
**Competition:** Samsung PRISM XR Hackathon 2026 — Track 4  
**Date:** November 2026  

---

## 1. Architectural Constraints & Tradeoffs

Developing an action-aware video summarization pipeline for egocentric XR presents unique constraints:
1. **First-Person Dynamics:** Egocentric footage features rapid camera ego-motion, frequent head rotations, dynamic hand-object occlusion, and severe motion blur.
2. **Resource Constraints:** In XR headset runtimes and hackathon evaluation environments, GPU acceleration is not guaranteed. Inference must execute efficiently on standard x86-64 CPUs within a strict latency envelope (< 0.5x realtime).
3. **Dual Modality (Visual + Motion):** Pure 2D visual classification cannot distinguish between static presence and physical interaction (e.g., holding a knife vs. cutting an onion). Motion dynamics are essential for verb grounding.

---

## 2. Evaluation of Candidate Architectures

| Architecture | Parameters | FLOPs | CPU Latency (per frame) | Memory Footprint | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ResNet-50** | 25.6 M | 4.1 G | 85 ms | ~100 MB | Rejected: Too heavy for continuous CPU video decoding. |
| **EfficientNet-B0** | 5.3 M | 0.39 G | 32 ms | ~25 MB | Viable, but higher memory access latency during batching. |
| **MobileNetV3-Large** | 5.4 M | 0.22 G | 24 ms | ~22 MB | Viable, but overkill for concept feature pooling. |
| **MobileNetV3-Small (1.0x float)** | **2.5 M** | **0.06 G** | **9 ms** | **10.7 MB** | **SELECTED: Optimal CPU efficiency, low latency, rich representation.** |
| **Farneback Optical Flow** | Dense CV | N/A | 14 ms (downscaled) | < 5 MB | **SELECTED: Accurate physical motion energy, direction, and boundary snapping.** |

---

## 3. Justification for MobileNetV3-Small + Optical Flow Hybrid

1. **Lightweight Edge Deployment:**
   - MobileNetV3-Small uses depthwise separable convolutions, squeeze-and-excitation modules, and hard-swish non-linearities, delivering strong visual classification at only 2.5 million parameters.
   - At 224x224 input resolution, single-frame CPU inference executes in ~9 ms on standard hardware.

2. **Semantic Concept Grounding:**
   - Pretrained on ImageNet-1K, MobileNetV3 recognizes 1000 object and scene categories.
   - EgoWeave maps supported nouns (`knife`, `pan`, `pot`, `fridge`, `plate`, `cup`, `spoon`, `bottle`, `bowl`, `tap`, `food`, etc.) and activity labels (`bike`, `ski`, `surfing`, `boxing`, etc.) directly to ImageNet synsets using max-activation pooling across synonymous classes.

3. **Complementary Motion Gating:**
   - Farneback dense optical flow captures the kinetic profile of hand interactions:
     - High oscillation energy identifies periodic cutting and slicing.
     - Downward directional flow identifies liquid pouring.
     - Velocity transitions (motion valleys) mark natural hand pauses between discrete physical tasks.
