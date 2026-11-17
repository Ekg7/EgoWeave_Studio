# EgoWeave Studio — Implementation Plan & Phase Tracking

## Phase 0: Workspace & Specification Audit [COMPLETED]
- [x] Inspect existing workspace assets (`manifest.csv`, `supported_classes.json`, `TEAM_README.md`, `P02_109.json`, `skiing_03.json`).
- [x] Implement official `validate.py` validator adhering to all challenge constraints.
- [x] Setup runtime tools: Node.js v20.18.0 & npm 10.8.2 in `tools/node`.
- [x] Document challenge specification in `docs/CHALLENGE_SPEC.md` and audit in `docs/WORKSPACE_AUDIT.md`.

## Phase 1: Frontend Foundation [IN PROGRESS]
- [ ] Scaffold React 19 + TypeScript + Vite frontend in `frontend/`.
- [ ] Configure Tailwind CSS, dark XR design tokens, Lucide icons, and layout shell.
- [ ] Implement core views:
  - Overview Dashboard (`/`)
  - New Analysis Upload (`/workspace/new`)
  - Video Workspace (`/workspace/:videoId`) with synced HTML5 player, interactive timeline, React Flow graph, highlight inspector, and JSON viewer.
  - Video Library (`/library`)
  - Evaluation Lab (`/evaluation`)
  - System Settings (`/settings`)
- [ ] Verify frontend build and browser rendering.

## Phase 2: Backend Foundation
- [ ] Scaffold FastAPI backend in `backend/`.
- [ ] Implement database models & SQLite persistence for videos and jobs.
- [ ] Implement REST endpoints:
  - `POST /api/v1/videos` (multipart MP4 upload & validation)
  - `GET /api/v1/videos` (library listing)
  - `GET /api/v1/videos/{video_id}` (metadata & status)
  - `GET /api/v1/jobs/{job_id}/events` (SSE real-time status streaming)
  - `GET /api/v1/videos/{video_id}/result` (full interactive result)
  - `GET /api/v1/videos/{video_id}/result.json` (official 6-key competition JSON)
  - `GET /api/v1/videos/{video_id}/highlight.mp4` (compiled video highlight)
  - `GET /api/v1/health` (service health & GPU info)
- [ ] Implement background worker queue and job progress dispatching.

## Phase 3: Complete Full-Stack Integration
- [ ] Connect React frontend to FastAPI backend using TanStack Query and SSE hooks.
- [ ] Test end-to-end flow: Video upload $\rightarrow$ SSE progress updates $\rightarrow$ workspace display with real timeline and graph.
- [ ] Verify highlight video export and official JSON download.

## Phase 4: Action Recognition & Computer Vision Pipeline
- [ ] Implement `inference/video_loader.py` for robust video decoding.
- [ ] Implement `inference/preprocessing.py` for adaptive frame sampling and motion energy estimation.
- [ ] Implement `inference/action_recognition.py` with multi-scale sliding windows (1.5s, 3.0s, 5.0s) and EPIC verb-noun pair priors.
- [ ] Implement temporal non-maximum suppression (NMS) and boundary refinement.

## Phase 5: Interaction Graph & Summarization
- [ ] Implement `inference/event_graph.py` (NetworkX graph linking chronological events, common tools/objects, and action similarity).
- [ ] Implement `inference/importance_scoring.py` combining optical flow / motion energy, actionness, and visual novelty.
- [ ] Implement `inference/highlight_optimizer.py` (greedy submodular knapsack enforcing $\le 15\%$ budget and $\ge 4.0\text{s}$ segment constraints).
- [ ] Implement `inference/category_classifier.py` for FPVSum activity classification across 16 supported classes.
- [ ] Implement `inference/serializer.py` strictly generating compliant 6-key output JSON.

## Phase 6: Evaluation Lab & Experiments
- [ ] Build standalone evaluation suite calculating Action mAP, Action Coverage, Highlight F1, and Label Accuracy.
- [ ] Populate `docs/EXPERIMENT_LOG.md` and `docs/EVALUATION_RESULTS.md`.

## Phase 7 & 8: Packaging, Docker & Final Polish
- [ ] Create official `run.sh` and Windows-compatible `run.ps1` (`./run.sh <video.mp4> <out.json>`).
- [ ] Validate generated outputs with `python validate.py --dir outputs/`.
- [ ] Write Dockerfile and docker-compose.yml for reproducible submission.
- [ ] Create comprehensive `README.md` and project demonstration assets.

