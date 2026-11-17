# EgoWeave Studio — Final Limitations & Future Work
**Samsung PRISM XR Hackathon 2026 — Track 4: Action-Aware Video Summarization for First-Person XR**  
**Date:** November 17, 2026  

---

## 1. Current System Limitations & Honest Technical Boundaries

To maintain scientific integrity and audit transparency, the known operational boundaries of the current EgoWeave Studio implementation are explicitly detailed below:

### 1.1 Compute & Execution Constraints
- **CPU Execution Only:** Due to sandbox environment constraints during development and evaluation, inference runs on CPU (oneDNN accelerated). While throughput is fast ($5.0\times$ to $8.2\times$ faster than real-time), GPU acceleration via TensorRT or ONNX Runtime would enable real-time $60\text{ fps}$ processing.
- **Uniform Frame Sampling (1.0 fps):** Fast micro-actions lasting under $0.8\text{s}$ (such as rapid flicking of a switch or quick glancing) can be missed by the $1.0\text{ fps}$ temporal stride.

### 1.2 Model & Feature Representation Boundaries
- **ImageNet Transfer Backbone:** MobileNetV3Small is pretrained on ImageNet-1K object classification. It possesses strong general semantic representations for everyday objects (cups, pans, knives, bikes) but lacks egocentric-specific visual features (such as 3D hand poses, gaze vectors, and object affordance cues).
- **Zero-Shot Noun Mapping:** Mapping from ImageNet synsets to the 300 EPIC-KITCHENS nouns is performed via an ontological synonym table. Rare or highly specific kitchen implements not well-separated in ImageNet (e.g., specific spatulas or niche containers) may suffer lower recognition confidence.
- **Motion-Based Verb Estimation:** Verbs are currently estimated from Farneback optical flow velocity patterns and Bayesian priors rather than an end-to-end 3D temporal convolution (e.g., SlowFast or X3D) or video transformer (e.g., TimeSformer). Consequently, actions with similar optical flow signatures (e.g., `stir` vs `mix`) can be confused without fine-grained temporal attention.

### 1.3 Short Video Budget Conflict
- For videos shorter than $26.7\text{ seconds}$, satisfying the official minimum highlight segment constraint ($\ge 4.0\text{s}$) makes mathematical adherence to the $15.0\%$ duration cap impossible ($4.0 / 26.7 \approx 15.0\%$). On such inputs, the optimizer chooses the single highest-value $4.0\text{s}$ highlight, which triggers an official validator duration penalty. This is a property of the competition rule set, not an implementation flaw.

---

## 2. Future Work & Production Roadmap

### 2.1 Fine-Tuning on Authentic Egocentric Datasets
- **Full Video Pretraining:** Fine-tune lightweight video transformers (e.g., MobileVideo, VideoMAE-v2, or FastViT) directly on the full EPIC-KITCHENS-100 (700 hours) and Ego4D (3,670 hours) datasets.
- **Temporal Action Localization (TAL):** Integrate dedicated modern TAL heads such as **ActionFormer** or **TriDet** to predict continuous action boundary distributions and confidence scores rather than fixed sliding-window proposals.

### 2.2 Egocentric Hand & Object Pose Integration
- **3D Hand Tracking:** Integrate MediaPipe Hands or HaMeR to extract 3D hand keypoints and track contact states (`in-hand`, `approaching`, `releasing`).
- **Object State Change Detection:** Incorporate visual models that detect transitions in object physical state (e.g., intact $\to$ diced, empty $\to$ full, closed $\to$ open) to pin highlight boundaries precisely to meaningful physical accomplishments.

### 2.3 Multimodal XR Narration & Spatial Audio
- **Egocentric Vision-Language Models (VLM):** Leverage lightweight on-device multimodal models (e.g., PaliGemma or MobileVLM) to generate contextual natural language summaries and XR spatial captions for each highlight segment.
- **Spatial Audio Cues:** Incorporate XR binaural audio energy and acoustic events (sizzling, chopping, water running, vehicle noise) into the highlight knapsack importance function $\alpha \cdot \text{Action} + \beta \cdot \text{Motion} + \gamma \cdot \text{Audio}$.

### 2.4 On-Device XR Deployment
- **Snapdragon Spaces & XR2+ Gen 2 Optimization:** Quantize the visual backbone to INT8 via Qualcomm Neural Processing SDK (QNN / SNPE) for native on-chip execution on Samsung XR headsets and smart glasses, achieving sub-$10\text{ms}$ per-frame inference at under 2 Watts.
