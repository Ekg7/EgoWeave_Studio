# EgoWeave Studio — AI Architecture Specification (Mission 4)
**Project:** EgoWeave Studio — Samsung PRISM XR Hackathon 2026 (Track 4)  
**Date:** 2026-11-16  
**Status:** Approved for Implementation & Training  

---

## 1. System Overview & Representation Flow

EgoWeave Studio employs a modular two-stream architecture combining a deep spatial feature extractor (MobileNetV3-Small) with temporal optical flow dynamics and task-specific classification heads for verbs, nouns, and video activity categories.

```text
Input Video Frame Sequence (224x224 RGB, 2.0 FPS)
                     │
       ┌─────────────┴─────────────┐
       ▼                           ▼
MobileNetV3-Small Backbone    Dense Optical Flow (Farneback)
(Penultimate Activation 18)   • Mean Local Magnitude
• 1024-d Deep Visual Vector   • Median Camera Motion Subtraction
• 1000-d ImageNet Probs       • Temporal Energy & Acceleration (64-d)
       │                           │
       ├───────────────────────────┤
       ▼                           ▼
[Noun Head Input: 1024-d]   [Verb Head Input: 1024 + 64 = 1088-d]
Dense(256) + LayerNorm       Dense(256) + LayerNorm
Dropout(0.20)                Dropout(0.20)
Dense(301, Softmax)          Dense(98, Softmax)
       │                           │
       ▼                           ▼
301 Supported Noun Probs    98 Supported Verb Probs
       │                           │
       └─────────────┬─────────────┘
                     ▼
        Joint Action Compatibility
        P(v, n) = P(v) * P(n) * Prior(v, n)
                     │
                     ▼
        Temporal Boundary Refinement & NMS
```

---

## 2. Tensor Dimensions & Layer Specifications

### A. Feature Extraction Backbone
- **Base Network:** MobileNetV3-Small (depth multiplier = 1.0).
- **Input Tensor:** $\mathbf{X} \in \mathbb{R}^{B \times 224 \times 224 \times 3}$, normalized to $[-1.0, 1.0]$.
- **Penultimate Feature Layer:** `activation_18` (Conv2D pointwise projection).
- **Extracted Feature Vector:** $\mathbf{z} \in \mathbb{R}^{B \times 1024}$.
- **Parameters:** 2,542,856 weights (frozen ImageNet transfer backbone).

### B. Noun Classification Head (`NounHead`)
- **Objective:** Predict object identity from the official 301-class EPIC-KITCHENS vocabulary.
- **Input:** Visual feature vector $\mathbf{z} \in \mathbb{R}^{1024}$.
- **Layers:**
  1. `Dense(256, activation='relu', kernel_regularizer=L2(1e-4))`
  2. `LayerNormalization()`
  3. `Dropout(0.20)`
  4. `Dense(301, activation='softmax')`
- **Output:** $\mathbf{p}_{\text{noun}} \in [0, 1]^{301}$, $\sum_{i} p_i = 1.0$.
- **Parameter Count:** $(1024 \times 256 + 256) + 512 + (256 \times 301 + 301) = 340,333$ parameters.

### C. Verb Classification Head (`VerbHead`)
- **Objective:** Predict interaction verbs from the official 98-class EPIC-KITCHENS vocabulary.
- **Input:** Concatenated visual-motion representation $\mathbf{h} = [\bar{\mathbf{z}} \,\|\, \mathbf{m}] \in \mathbb{R}^{1088}$.
  - $\bar{\mathbf{z}} \in \mathbb{R}^{1024}$: Average-pooled visual embedding over the temporal window.
  - $\mathbf{m} \in \mathbb{R}^{64}$: Motion feature embedding (flow magnitude stats, orientation histogram, acceleration).
- **Layers:**
  1. `Dense(256, activation='relu', kernel_regularizer=L2(1e-4))`
  2. `LayerNormalization()`
  3. `Dropout(0.20)`
  4. `Dense(98, activation='softmax')`
- **Output:** $\mathbf{p}_{\text{verb}} \in [0, 1]^{98}$, $\sum_{j} p_j = 1.0$.
- **Parameter Count:** $(1088 \times 256 + 256) + 512 + (256 \times 98 + 98) = 304,994$ parameters.

### D. FPVSum Video Category Head (`CategoryHead`)
- **Objective:** Classify video-level activity across the 16 supported classes.
- **Input:** Video-wide globally pooled visual feature $\mathbf{v} = \frac{1}{T} \sum_{t=1}^T \mathbf{z}_t \in \mathbb{R}^{1024}$.
- **Layers:**
  1. `Dense(128, activation='relu')`
  2. `Dropout(0.25)`
  3. `Dense(16, activation='softmax')`
- **Output:** $\mathbf{p}_{\text{cat}} \in [0, 1]^{16}$.
- **Parameter Count:** $(1024 \times 128 + 128) + (128 \times 16 + 16) = 133,408$ parameters.

---

## 3. Training Objectives & Loss Formulations

1. **Noun & Verb Classification:**
   Categorical Cross-Entropy with label smoothing ($\alpha = 0.05$) to mitigate long-tailed overconfidence:
   $$\mathcal{L}_{\text{cls}} = -\sum_{k=1}^K y_k^{\text{smooth}} \log \hat{y}_k$$
   where $y_k^{\text{smooth}} = (1 - \alpha) y_k + \frac{\alpha}{K}$.
2. **Focal Loss Weighting for Rare Nouns:**
   For imbalanced classes, focal modulation $\gamma = 1.5$:
   $$\mathcal{L}_{\text{focal}} = -\sum_{k=1}^K (1 - \hat{y}_k)^\gamma y_k \log \hat{y}_k$$
3. **Optimization:**
   - Optimizer: Adam with weight decay ($1 \times 10^{-4}$).
   - Initial Learning Rate: $1 \times 10^{-3}$ with cosine annealing schedule.
   - Batch Size: 32.

---

## 4. Inference Pipeline Integration & Fallback Guarantees

- **Primary Pipeline Path:**
  If task-specific weights (`weights/noun_head_weights.npz`, `weights/verb_head_weights.npz`, `weights/category_head_weights.npz`) exist on disk, the model loads them and computes forward passes using the trained weights.
- **Deterministic Fallback:**
  If trained head weights are absent, the system gracefully falls back to the neuro-symbolic affordance and concept projection engine, logging an explicit warning without silent degradation.

