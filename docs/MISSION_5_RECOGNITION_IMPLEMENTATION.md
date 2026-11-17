# EgoWeave Studio — Mission 5 Recognition Architecture & Implementation Report
**Samsung PRISM XR Hackathon 2026 — Track 4: Action-Aware Video Summarization**  
*Document Version: 1.0*  
*Audit Date: November 17, 2026*

---

## 1. Architectural Overview

EgoWeave Studio employs an interaction-graph-guided, neuro-symbolic computer vision architecture designed for real-time egocentric video understanding on edge/CPU hardware:

```
[Raw First-Person Video Frames]
               │
       ┌───────┴────────────────────────┐
       ▼                                ▼
[Deep Neural Vision]           [Motion Dynamics]
MobileNetV3-Small              Farneback Optical Flow
(ImageNet-1K Pretrained)       (Median Ego-Motion Subtraction)
       │                                │
       ▼                                ▼
[Visual Concept Activations]   [Local Kinematic Energy & Novelty]
(301 Nouns & 16 Categories)    (Radial Divergence & Flow Magnitude)
       │                                │
       └───────────────┬────────────────┘
                       ▼
        [Boundary-Snapped Temporal Proposals]
        Multi-Scale Sliding Windows (2.0s, 4.0s, 6.0s)
        Local Optical Flow Minima Snapping
                       ▼
        [Bayesian Verb-Noun Prior Matrix]
        P(Verb | Noun) Co-occurrence Scoring
                       ▼
        [Temporal Non-Maximum Suppression (NMS)]
        tIoU Threshold = 0.30
                       ▼
        [Controlled Segment Merging]
        max_gap = 0.8s, max_duration = 8.0s
                       ▼
        [Temporal Interaction Graph & Highlight Optimizer]
        Coverage-Aware Dynamic Budget Allocation (<= 15.0%)
```

---

## 2. Detailed Technical Components

### A. Deep Neural Backbone & Semantic Mapping
* **Backbone:** MobileNetV3-Small (`weights_mobilenet_v3_small_224_1.0_float.h5`, 2.54M parameters, 10.24 MB).
* **Frame Resolution:** Resized to $224 \times 224 \times 3$, normalized to $[-1, 1]$.
* **Semantic Mapping:** Maps ImageNet-1K class probabilities to domain nouns (knife, pan, pot, fridge, plate, cup, spoon, fork, onion, tap, etc.) and activity categories via canonical WordNet synset mappings.

### B. Kinematic Optical Flow & Ego-Motion Compensation
* **Flow Algorithm:** OpenCV dense Farneback optical flow (`pyr_scale=0.5, levels=2, winsize=15, iterations=2`).
* **Camera Stabilization:** In first-person video, wearer head movements induce dominant global flow. We subtract median horizontal and vertical flow vectors $(\bar{u}, \bar{v})$ across the frame:
  $$u_{\text{comp}} = u - \text{median}(u), \quad v_{\text{comp}} = v - \text{median}(v)$$
  leaving local hand-object motion energy.

### C. Motion-Valley Boundary Snapping (New in Mission 5)
* In egocentric interactions, humans naturally pause or reverse velocity before and after touching an object.
* `_snap_to_motion_valley(t, motion_profile, window=0.5)` inspects a $\pm 0.5\text{s}$ neighborhood and snaps window boundaries to the local optical flow minimum, tightening segment bounds around actual actions.

### D. Multi-Scale Windowing & Bayesian Scoring
* Sliding window scales of $2.0\text{ s}$, $4.0\text{ s}$, and $6.0\text{ s}$ with a stride of $1.0\text{ s}$.
* Joint candidate score combines visual confidence, motion dynamics, and Bayesian pair priors:
  $$S(v, n) = 0.30 \cdot \text{actionness} + 0.35 \cdot \text{noun\_conf} + 0.35 \cdot (\text{affordance}(v) \times P(v \mid n))$$

### E. Controlled Adjacent Merging
* Previous versions merged actions up to $35\text{ s}$, which collapsed multiple fine-grained events into giant intervals and caused Action mAP to drop to 0.
* Mission 5 constrains `max_gap = 0.8\text{ s}` and `max_duration = 8.0\text{ s}`, producing realistic, discrete action segments typical of first-person interactions.
