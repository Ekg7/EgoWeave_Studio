# EgoWeave Studio
### Action-Aware Video Summarization for First-Person XR
**Samsung PRISM XR Hackathon 2026 — Track 4**

> *"From raw first-person video to a structured, action-aware XR highlight reel."*

---

## 1. Executive Summary

**EgoWeave Studio** is an action-aware egocentric video intelligence and summarization platform developed for Samsung PRISM XR Hackathon 2026 (Track 4). First-person video captured from smart glasses or XR headsets features persistent head motion, jitter, and long stretches of low-activity video. 

EgoWeave moves beyond basic scene-cut detection by combining deep visual perception (MobileNetV3), dense motion dynamics (Farneback optical flow), Bayesian verb-noun priors, and a constrained dynamic programming knapsack optimizer. The platform extracts meaningful human actions, classifies high-level activities, constructs an interactive temporal interaction graph, and selects concise highlights strictly respecting the **$\le 15.0\%$ duration budget** and **$\ge 4.0\text{s}$ segment length** constraints.

---

## 2. Quickstart & Submission Run Contracts

EgoWeave satisfies the official competition CLI specification for single-command evaluation:

### Linux / macOS
```bash
chmod +x run.sh
./run.sh <input_video.mp4> <output_submission.json>
```

### Windows (PowerShell)
```powershell
powershell -ExecutionPolicy Bypass -File run.ps1 <input_video.mp4> <output_submission.json>
```

### Official Output Validation
```bash
python validate.py --dir outputs/ -v
```

---

## 3. Audited Empirical Performance & Benchmarks

In accordance with competition integrity standards, all reported metrics derive from audited execution on real video data using authentic pretrained checkpoints (`weights/keras_cache/models/weights_mobilenet_v3_small_224_1.0_float.h5`).

### Pilot Benchmark Summary
| Video ID | Dataset Type | Duration | Latency | Real-Time Factor | Highlight F1 | Label Acc | Action Cov | Score |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `test_demo.mp4` | EPIC-KITCHENS | 15.0s | 1.81s | **8.28x** | 100.0% | 100.0% | 0.0% | **39.17 / 100** |
| `test_120s.mp4` | EPIC-KITCHENS | 120.0s | 23.74s | **5.05x** | 0.0% | 100.0% | 40.0% | **26.00 / 100** |
| **Combined** | **Multi-Scale** | **135.0s** | **25.55s** | **5.28x** | **50.0%** | **100.0%** | **20.0%** | **32.59 / 100** |

- **Real-Time Speedup:** $5.05\times$ to $8.28\times$ faster than real-time on CPU (mean throughput: $5.28\times$).
- **Budget Compliance Rate:** $100\%$ across all standard-duration clips ($\ge 27\text{s}$).

---

## 4. Key Architectural Features

1. **Lightweight Deep Perception:** MobileNetV3Small feature extractor running on CPU with oneDNN acceleration, generating 1024-D embeddings at 1.0 fps.
2. **Dense Motion Profiling:** Farneback dense optical flow tracking hand/head velocity variance and acceleration.
3. **Bayesian Action Formulation:** Evaluates candidate interactions via log-odds Bayesian pairing:
   $$\text{Score}(\text{action}) = \text{Score}_{\text{noun}} \times \text{Score}_{\text{verb}} \times P(\text{verb} \mid \text{noun})$$
4. **Motion Valley Boundary Snapping:** Temporal proposals snap to local optical flow minima ($\pm 0.5\text{s}$) to match natural interaction boundaries.
5. **Coverage-Aware Knapsack Optimizer:** Formulates highlight selection as a 0/1 knapsack problem with interval memoization, guaranteeing $\le 15.0\%$ total duration and $\ge 4.0\text{s}$ segment durations.
6. **Temporal Interaction Graph:** Models actions, tools, and objects as a directed acyclic graph (DAG), interactively rendered in React Flow.
7. **Full-Stack Application:** FastAPI backend with SQLite persistence and Server-Sent Events, coupled to a React 18 / TypeScript / Tailwind CSS web interface.

---

## 5. Output Specification (Track 4 Format)

Output JSON files strictly contain the 6 required top-level keys:
```json
{
  "team_id": "T07",
  "video_id": "P02_109",
  "duration_sec": 512.3,
  "label": {
    "name": "cooking",
    "score": 0.96
  },
  "actions": [
    {
      "segment": [12.4, 18.9],
      "verb": "open",
      "noun": "fridge",
      "score": 0.82
    }
  ],
  "highlights": [
    {
      "segment": [12.0, 23.0]
    }
  ]
}
```

---

## 6. Running the Full-Stack Web Application

### Prerequisites
- Python 3.10+ with dependencies installed (`pip install -r requirements.txt`)
- Node.js & npm (for building the React frontend; pre-built bundle is included in `frontend/dist`)

### Step 1: Start Backend Server
```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

### Step 2: Open Browser
Navigate to `http://localhost:8000`. The FastAPI backend serves the React SPA directly from `frontend/dist`.

---

## 7. Verification & Test Suite

Run the complete integration and regression suite:
```bash
# 1. Run unit and integration tests via pytest
python -m pytest backend/tests/test_api.py -v

# 2. Run live API endpoint checks
python backend/tests/run_live_tests.py

# 3. Validate all generated outputs
python validate.py --dir outputs/ -v
```

---

## 8. Technical Documentation Index

Detailed engineering and audit reports are located in `docs/`:
- [`FINAL_REPOSITORY_AUDIT.md`](docs/FINAL_REPOSITORY_AUDIT.md) — 14-stage code and pipeline audit.
- [`FINAL_ARCHITECTURE.md`](docs/FINAL_ARCHITECTURE.md) — Mathematical formulas, dataflows, and component design.
- [`FINAL_MODEL_EVALUATION.md`](docs/FINAL_MODEL_EVALUATION.md) — Empirical pilot metrics and benchmark analysis.
- [`FINAL_TEST_REPORT.md`](docs/FINAL_TEST_REPORT.md) — Regression test results and validator logs.
- [`FINAL_FILE_CLEANUP_REPORT.md`](docs/FINAL_FILE_CLEANUP_REPORT.md) — Repository hygiene and file provenance.
- [`FINAL_LIMITATIONS_AND_FUTURE_WORK.md`](docs/FINAL_LIMITATIONS_AND_FUTURE_WORK.md) — Current technical boundaries and production roadmap.
