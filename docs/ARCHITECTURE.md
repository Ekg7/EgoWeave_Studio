# EgoWeave Studio — System Architecture

## 1. System Overview
**EgoWeave Studio** is an action-aware video summarization and XR intelligence platform designed for first-person videos (EPIC-KITCHENS-100 and FPVSum). It extracts fine-grained verb-noun interactions, estimates temporal action boundaries, constructs an interactive temporal interaction graph, and generates concise, high-value highlights within a strict $15\%$ duration budget.

```
+----------------------------------------------------------------------------------------------------+
|                                      EGOWEAVE STUDIO FRONTEND                                      |
|  [Overview]  |  [New Analysis Upload]  |  [Interactive Workspace]  |  [Library]  |  [Evaluation]  |
|                                                                                                    |
|  +--------------------+  +----------------------+  +--------------------------------------------+  |
|  | Synced Video Player|  | React Flow Action    |  | Chronological Action Timeline & Highlights|  |
|  | (Custom Controls)  |  | Interaction Graph    |  | with Interactive Scrubbing & Jump-to-Event |  |
|  +--------------------+  +----------------------+  +--------------------------------------------+  |
+----------------------------------------------------------------------------------------------------+
                                      |                     ^
                                      | REST / SSE Stream   | JSON / Video Assets
                                      v                     |
+----------------------------------------------------------------------------------------------------+
|                                        FASTAPI BACKEND API                                         |
|  /api/v1/videos  |  /api/v1/jobs/{id}/events  |  /api/v1/videos/{id}/result  |  /api/v1/evaluation |
|                                                                                                    |
|  +--------------------+  +----------------------+  +--------------------------------------------+  |
|  | Video Storage &    |  | SQLite Job Database  |  | Server-Sent Events (SSE)                   |  |
|  | File Metadata      |  | & Execution Ledger   |  | Live Progress Dispatcher                   |  |
|  +--------------------+  +----------------------+  +--------------------------------------------+  |
+----------------------------------------------------------------------------------------------------+
                                      |
                                      | Unified Python Inference Engine
                                      v
+----------------------------------------------------------------------------------------------------+
|                                    EGOWEAVE INFERENCE ENGINE                                       |
|                                                                                                    |
|  +-----------------------------+     +-----------------------------+     +-----------------------+ |
|  | Video Decoding & Preprocess | --> | Multi-Scale Sliding Windows | --> | Action Pair Prior     | |
|  | (OpenCV / FFmpeg / PyAV)    |     | (1.5s, 3.0s, 5.0s Windows)  |     | P(v|w)*P(n|w)*Prior   | |
|  +-----------------------------+     +-----------------------------+     +-----------------------+ |
|                                                                                      |             |
|  +-----------------------------+     +-----------------------------+                 |             |
|  | Budgeted Highlight Selector | <-- | Temporal Interaction Graph  | <---------------+             |
|  | Submodular / Greedy Knapsack|     | (NetworkX Events & Object Edges)                            |
|  +-----------------------------+     +-----------------------------+                               |
|                 |                                                                                  |
|                 v                                                                                  |
|  +-----------------------------------------------------------------------------------------------+ |
|  | Serializer & Export: <video_id>.json (Official 6-Key Schema) & highlight.mp4 (FFmpeg Stream)  | |
|  +-----------------------------------------------------------------------------------------------+ |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Component Specifications

### 2.1 Frontend Architecture (`frontend/`)
- **Framework:** React 19 + TypeScript + Vite
- **Styling:** Tailwind CSS + Radix UI + Lucide Icons + Dark XR Theme
- **Data Fetching:** TanStack Query + Native Server-Sent Events (SSE)
- **Interactive Graph:** `@xyflow/react` (React Flow) rendering verb-noun interactions, temporal edges, and shared-noun dependencies.
- **Video Playback:** HTML5 `<video>` engine with custom precision scrubbing, keyboard shortcuts (Space, $\leftarrow$, $\rightarrow$), synchronized highlight markers, and action jump points.
- **Routes:**
  - `/`: Overview Dashboard with real statistics, recent videos, and quick actions.
  - `/workspace/new`: Drag-and-drop video upload with file validation and metadata inspection.
  - `/workspace/:videoId`: Multi-panel inspection studio (Player, Timeline, React Flow Graph, Highlight Inspector, JSON Viewer).
  - `/library`: Searchable, filterable library of processed first-person videos.
  - `/evaluation`: Challenge metrics lab (Action Coverage, Action mAP, Highlight F1, Label Accuracy).
  - `/settings`: System configuration, model weights info, and hardware execution status.

### 2.2 Backend Architecture (`backend/`)
- **Framework:** FastAPI with Pydantic v2 validation models.
- **Persistence:** SQLite (`egoweave.db`) storing videos, jobs, and analysis metadata.
- **Async Execution:** Asynchronous job runner with thread-pool offloading for compute-heavy CV inference.
- **Streaming:** Server-Sent Events (SSE) streaming real-time stage progression:
  1. `Extracting video metadata`
  2. `Sampling frames & optical flow analysis`
  3. `Detecting candidate verb-noun actions`
  4. `Building temporal interaction graph`
  5. `Optimizing coverage-aware highlight segments`
  6. `Compiling output JSON & rendering highlight MP4`
  7. `Completed`

### 2.3 Inference Engine (`inference/`)
- **`video_loader.py`:** Video decoding, frame timestamp calibration, and duration estimation.
- **`preprocessing.py`:** Frame sampling, image resizing, and optical flow / motion energy estimation.
- **`action_recognition.py`:** Multi-scale sliding window action classification using verb-noun priors derived from EPIC-KITCHENS-100 vocabulary.
- **`event_graph.py`:** NetworkX-based interaction graph linking chronological actions, recurrent verbs, and shared object manipulations.
- **`importance_scoring.py`:** Frame-level importance function combining local motion, actionness, and novelty.
- **`highlight_optimizer.py`:** Greedy submodular optimizer enforcing the $\le 15\%$ duration budget with $\ge 4.0\text{s}$ segment constraints.
- **`category_classifier.py`:** Video-level category classification mapping to the 16 supported classes.
- **`serializer.py`:** Strictly serializes to the official 6-key competition JSON schema.
- **`pipeline.py`:** Unified entry point invoked by both the FastAPI backend and `./run.sh <video.mp4> <out.json>`.

