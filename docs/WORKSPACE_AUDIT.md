# EgoWeave Studio — Workspace & Technical Audit
**Date:** 2026-11-16  
**Project:** Samsung PRISM XR Hackathon 2026 — Track 4 (Action-Aware Video Summarization for First-Person XR)

---

### 1. Starter Kit Assets & Verification
The starter kit files in the workspace have been examined and catalogued:
- `manifest.csv`: Contains 187 video entries (138 `epic_kitchens_100` validation videos, 49 `fpvsum` annotated videos) with duration in seconds.
- `supported_classes.json`:
  - **16 video-level labels:** `bike`, `bikepolo`, `boxing`, `cooking`, `horse`, `jumping`, `longboarding`, `motor`, `parkour`, `plane`, `rockclimbing`, `scuba`, `skate`, `ski`, `surfing`, `other`.
  - **98 fine-grained verbs:** `take`, `put`, `wash`, `open`, `close`, `insert`, `turn-on`, `cut`, `turn-off`, `pour`, `mix`, etc.
  - **301 nouns:** `pan`, `knife`, `door`, `plate`, `cup`, `spoon`, `fridge`, `water`, `drawer`, `counter`, etc.
- `P02_109.json`: Validated reference JSON for EPIC-KITCHENS-100 format.
- `skiing_03.json`: Reference JSON for FPVSum format. Note: Starter kit had `"name": "skiing"`, while canonical dictionary label is `"ski"`. Our validator and normalization engine map activity synonyms to canonical supported classes.
- `TEAM_README.md`: Comprehensive official specification for data sourcing, run contract, evaluation weights, and integrity policy.
- `validate.py`: Implemented in workspace root conforming strictly to the official validation rules (6 top-level keys, duration within $\pm0.5$s, score bounds $[0, 1]$, non-overlapping highlights, $\ge 4.0$s single segment requirement, $15\%$ highlight duration limit).

---

### 2. Runtime Environment & Tooling Audit
- **Host OS:** Windows (with WSL/Linux Docker compatibility for containerized submission).
- **Python:** Python 3.13.15 with PyPI packages:
  - Web & API: `fastapi 0.141.1`, `uvicorn 0.52.4`, `pydantic 2.13.5`, `starlette 1.6.0`, `httpx 0.28.1`, `python-multipart 0.0.32`
  - Vision & AI: `opencv-python 5.0.0.93`, `numpy 2.5.2`, `scipy 1.18.1`, `scikit-learn 1.9.0`, `onnxruntime 1.31.0`, `mediapipe 1.0.1`, `tensorflow 2.21.0`
  - Data & Visualization: `pandas 3.0.5`, `matplotlib 3.11.1`, `networkx`
  - Testing: `pytest 9.1.1`
- **Node.js & NPM:** Node.js v20.18.0 LTS & npm 10.8.2 configured in local workspace `tools/node`.
- **FFmpeg & FFprobe:** Installed in `tools/ffmpeg` providing fast native video decoding, keyframe extraction, audio stripping, and highlight segment concatenation.

---

### 3. Identified Architectural Invariants
1. **Schema Separation:** The official submission JSON format (`video_id.json`) must strictly contain only the 6 required keys. Internal rich graph data, temporal transition edges, and frame embeddings must be served via dedicated API endpoints (`/api/v1/videos/{video_id}/result`) to power the React Flow interaction graph and timeline UI.
2. **Budget Safety Margin:** Highlights must stay under $15\%$ total duration ($14.0\% - 14.8\%$ target) to avoid length penalties in Action Coverage.
3. **Dual Pipeline Execution:** Both the web platform and the `./run.sh <video.mp4> <out.json>` CLI entrypoint must invoke the identical core inference pipeline (`inference/pipeline.py`), ensuring $100\%$ reproducibility.

