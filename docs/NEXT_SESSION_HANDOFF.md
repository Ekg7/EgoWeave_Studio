# EgoWeave Studio — Next Session Handoff & Maintenance Guide

**Project:** EgoWeave Studio  
**Competition:** Samsung PRISM XR Hackathon 2026 — Track 4  
**Date:** November 2026  

---

## 1. Project State at Handoff

- **Application Health:** Fully functional, tested, and competition-ready full-stack application (FastAPI + React 18.3 + SQLite).
- **Recent Test Findings (EXP-06, P23_01.mp4):**
  - Confirmed that pipeline processes 91.86s videos, extracts optical flow motion valleys, constructs graphs, and renders highlights.
  - Confirmed that static 2D ImageNet-1K MobileNetV3 cannot recognize fine-grained actions (e.g. `cut onion`) due to vocabulary and temporal absence.
  - Formulated the exact data and model recommendation: download small subset (5 videos, ~2.5 GB) + pretrained EPIC-KITCHENS-100 SlowFast / TSM checkpoint (~150 MB).
- **Test Pass Rate:**
  - `pytest backend/tests/test_api.py`: 5/5 PASSED.
  - `python backend/tests/run_live_tests.py`: 5/5 PASSED.
  - `python validate.py --dir outputs/ -v`: 100% PASSED.

---

## 2. Quick Execution Guide

### Starting the Integrated Full-Stack Server
From workspace root:
```powershell
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```
Open browser to: `http://localhost:8000`

### Running Single-Video Inference via CLI
```powershell
powershell -ExecutionPolicy Bypass -File run.ps1 <path_to_video.mp4> <path_to_output.json>
```

### Validating Submission JSON Files
```powershell
python validate.py --dir outputs/ -v
```

### Running Test Suites
```powershell
python -m pytest backend/tests/test_api.py -v
python backend/tests/run_live_tests.py
```
