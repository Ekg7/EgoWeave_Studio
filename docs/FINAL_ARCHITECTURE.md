# EgoWeave Studio — Final Architecture Specification
**Samsung PRISM XR Hackathon 2026 — Track 4: Action-Aware Video Summarization for First-Person XR**  
**Date:** November 17, 2026  

---

## 1. Architectural Vision & Core Principles

EgoWeave Studio addresses the core challenge of **Action-Aware Video Summarization for First-Person XR**. In egocentric video captured from head-mounted displays or smart glasses, traditional summarization methods that rely purely on scene-cut detection or visual clustering fail because:
1. Egocentric video is characterized by continuous camera motion, head turns, and jitter.
2. The primary semantic signal is conveyed by **fine-grained hand-object interactions** (verbs and nouns), not background scene changes.
3. Users requiring summaries for XR playback have strict cognitive and temporal budgets ($\le 15.0\%$ of original video length) with minimum clip coherence ($\ge 4.0\text{s}$).

EgoWeave Studio resolves this through a **multi-stage, perception-to-decision pipeline**:
```
                      ┌───────────────────────────────────────────────┐
                      │              Input Video (MP4)                │
                      └──────────────────────┬────────────────────────┘
                                             │
                      ┌──────────────────────▼────────────────────────┐
                      │    Video Loader & Preprocessing (OpenCV)       │
                      │  - Temporal frame sampling @ 1.0 fps          │
                      │  - Dual-resolution: 224x224 RGB / Grayscale   │
                      │  - Farneback dense optical flow               │
                      └──────────────────────┬────────────────────────┘
                                             │
                      ┌──────────────────────▼────────────────────────┐
                      │     Perception Tier (Feature Extraction)      │
                      │  - MobileNetV3Small (ImageNet pretrained)     │
                      │  - Global Average Pooling -> 1024-D feature   │
                      │  - ImageNet synset to noun candidate mapping  │
                      └──────────────────────┬────────────────────────┘
                                             │
                      ┌──────────────────────▼────────────────────────┐
                      │   Action Recognition & Temporal Localization  │
                      │  - Multi-scale proposal windows (2s, 4s, 6s)  │
                      │  - Motion dynamics & velocity thresholds      │
                      │  - Bayesian log-odds prior P(verb | noun)     │
                      │  - Temporal non-maximum suppression (NMS)     │
                      │  - Boundary snapping to motion valleys        │
                      └──────────────────────┬────────────────────────┘
                                             │
                      ┌──────────────────────▼────────────────────────┐
                      │     Semantic Structuring & Category Label     │
                      │  - Temporal Interaction DAG (React Flow)      │
                      │  - Video-level 16-class activity classifier   │
                      └──────────────────────┬────────────────────────┘
                                             │
                      ┌──────────────────────▼────────────────────────┐
                      │     Highlight Optimizer (Knapsack DP)         │
                      │  - Composite Importance Score (Action+Motion) │
                      │  - Constraint: Total duration <= 15.0%        │
                      │  - Constraint: Each segment >= 4.0s           │
                      │  - Chronological sorting & non-overlapping    │
                      └──────────────────────┬────────────────────────┘
                                             │
                      ┌──────────────────────▼────────────────────────┐
                      │       Serialization & Presentation Tier       │
                      │  - Official 6-key Track 4 JSON Serializer     │
                      │  - FFmpeg highlight video concatenation       │
                      │  - FastAPI REST API + SQLite Persistence      │
                      │  - React 18 / Tailwind / React Flow Web App   │
                      └───────────────────────────────────────────────┘
```

---

## 2. Deep Dive: Component Architectures

### 2.1 Video Loading & Preprocessing (`inference/preprocessing.py`, `inference/video_loader.py`)
- **Frame Sampling:** Frames are sampled uniformly at 1.0 fps. This sampling rate captures deliberate human interactions (which typically span 1.5–6.0 seconds) while minimizing redundant frame computations.
- **Dual-Stream Processing:**
  - **RGB Stream:** Frames are resized to $224 \times 224 \times 3$, normalized to $[-1, 1]$, and routed to the deep neural backbone.
  - **Motion Stream:** Successive frames are downscaled and converted to grayscale for Farneback dense optical flow computation (`pyr_scale=0.5, levels=3, winsize=15, iterations=3, poly_n=5, poly_sigma=1.2`). Flow magnitude is aggregated across grid spatial cells to produce a temporal motion energy vector $M(t)$.

### 2.2 Visual Representation (`inference/visual_backbone.py`)
- **Backbone Architecture:** MobileNetV3Small with hard-swish activations and squeeze-and-excitation blocks.
- **Model Checkpoint:** `weights/keras_cache/models/weights_mobilenet_v3_small_224_1.0_float.h5` (10,734,624 bytes). Verified against official Keras/TensorFlow distribution MD5 hash.
- **Feature Extraction:** Outputs a 1024-dimensional feature embedding per sampled timestamp.
- **Taxonomy Bridging:** Softmax output over ImageNet-1K is mapped onto the 300 supported EPIC-KITCHENS nouns using an ontological synset lookup table (`weights/imagenet_class_index.json`).

### 2.3 Action Recognition & Localization (`inference/action_recognition.py`)
- **Proposal Generation:** Multi-scale temporal windows of lengths $w \in \{2.0, 4.0, 6.0\}$ seconds are slid across the temporal feature sequence with a stride of 1.0 second.
- **Verb Estimation:** Action verbs are hypothesized based on the temporal motion profile (velocity variance, acceleration, directionality) and categorized into motion classes (e.g., `cut`, `wash`, `open`, `take`, `put`).
- **Bayesian Prior Integration:** To eliminate physically nonsensical predictions (e.g. `cut spoon` or `wash pan` with zero water motion), action candidates are scored using log-odds Bayesian pairing:
  $$\text{Score}(\text{action}) = \text{Score}_{\text{noun}} \times \text{Score}_{\text{verb}} \times P(\text{verb} \mid \text{noun})$$
- **Boundary Snapping to Motion Valleys:** Candidate temporal boundaries are refined by searching within a $\pm 0.5\text{s}$ neighborhood for local minima in optical flow magnitude:
  $$t_{\text{boundary}}^* = \arg\min_{t \in [t - 0.5, t + 0.5]} M(t)$$
  This aligns segment start and end points with natural preparation and cessation of hand movements.
- **Temporal NMS & Merging:** Overlapping proposals with $\text{IoU} > 0.4$ are suppressed, and adjacent proposals with identical verb-noun signatures separated by $\le 0.8\text{s}$ are merged up to a maximum duration of $8.0\text{s}$.

### 2.4 Highlight Optimizer (`inference/highlight_optimizer.py`)
The highlight selector formulates summarization as a **Constrained Multi-Attribute 0/1 Knapsack Problem**:
- **Candidate Pool:** Contiguous temporal segments of length $L \in [4.0, 10.0]$ seconds sampled across the video.
- **Importance Scoring:**
  $$I(s) = \alpha \cdot \text{ActionDensity}(s) + \beta \cdot \text{MeanMotion}(s) + \gamma \cdot \text{VisualNovelty}(s)$$
  where $\alpha = 0.50$, $\beta = 0.30$, and $\gamma = 0.20$.
- **Constraints:**
  1. $\sum_{s \in H} \text{duration}(s) \le 0.15 \times \text{duration}_{\text{total}}$
  2. $\forall s \in H, \text{duration}(s) \ge 4.0\text{ s}$
  3. $\forall s_i, s_j \in H \ (i \neq j), [t_{\text{start}}^i, t_{\text{end}}^i] \cap [t_{\text{start}}^j, t_{\text{end}}^j] = \emptyset$
  4. Chronologically sorted: $t_{\text{start}}^{i+1} > t_{\text{end}}^i$
- **Solver:** Dynamic programming with interval memoization, followed by greedy boundary extension to maximize budget utilization without violating caps.

### 2.5 Temporal Interaction Graph (`inference/interaction_graph.py`)
EgoWeave constructs a structured Temporal Interaction Directed Acyclic Graph (DAG):
- **Nodes:**
  - `ActionNode`: Represents a detected verb-noun action interval.
  - `ObjectNode`: Represents an interacted physical entity.
  - `ActivityNode`: Represents the video-level activity domain.
- **Edges:**
  - `TargetEdge`: Connects `ActionNode` $\to$ `ObjectNode`.
  - `SequenceEdge`: Connects consecutive actions $A_t \to A_{t+1}$ with temporal gap attribute $\Delta t$.
  - `SubActionEdge`: Connects `ActivityNode` $\to$ `ActionNode`.
- The resulting DAG is exported in JSON format and rendered interactively in the web UI using **React Flow**.

---

## 3. Full-Stack Web Architecture

### 3.1 Backend Service (`backend/app/`)
- **Framework:** FastAPI with asynchronous event loop.
- **Database:** SQLite (`backend/storage/egoweave.db`) with schema for video metadata, processing jobs, analysis submissions, and interaction graphs.
- **Job Management:** Asynchronous background processing worker with Server-Sent Events (SSE) broadcasting real-time progress percentages to connected clients.
- **Static Asset Serving:** Directly mounts `frontend/dist/assets` and serves `index.html` on root and client-side route paths, enabling single-binary or single-process deployment on port 8000.

### 3.2 Frontend Application (`frontend/src/`)
- **Framework:** React 18.3, TypeScript, Vite, Tailwind CSS.
- **Key Modules:**
  - `VideoPlayer`: Custom video controller with frame-accurate scrubbing and dual playback (original video vs. compiled highlight reel).
  - `ActionTimeline`: Interactive multi-track timeline displaying detected actions, confidence bars, and highlight segment overlays.
  - `InteractionGraphView`: Interactive canvas using React Flow displaying the temporal interaction graph with pan, zoom, and node filtering.
  - `HighlightManager`: Inspector for individual highlight intervals with play-segment functionality and duration budget meter.
  - `EvaluationLab`: Live benchmarking interface displaying Track 4 metrics, category confusion matrix, and one-click JSON export.

---

## 4. Submission & CLI Interfaces

- **CLI Runner:**
  - `run.sh <input_video.mp4> <output_submission.json>` (Linux/macOS)
  - `run.ps1 <input_video.mp4> <output_submission.json>` (Windows PowerShell)
- **Validation:**
  - `validate.py --dir outputs/ -v` strictly checks:
    1. Top-level keys (`team_id`, `video_id`, `duration_sec`, `label`, `actions`, `highlights`).
    2. Label structure (`name` in supported taxonomy, `score` in $[0, 1]$).
    3. Action segments ($t_0 < t_1$, non-overlapping, valid verb and noun).
    4. Highlight budget ($\sum \le 15\%$, single segment $\ge 4.0\text{s}$, chronological, non-overlapping).
