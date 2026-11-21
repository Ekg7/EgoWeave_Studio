# EgoWeave Studio — Next Session Handoff & Maintenance Guide

**Project:** EgoWeave Studio  
**Competition:** Samsung PRISM XR Hackathon 2026 — Track 4  
**Date:** November 2026  

---

## 1. Project State at Handoff

- **Application Health:** Fully functional, tested, and competition-ready full-stack application (FastAPI + React 18.3 + SQLite).
- **Recent Breakthroughs & Verification (EXP-07):**
  - Downloaded official EPIC-KITCHENS-100 annotations and verified 0% data leakage against `student_kit/manifest.csv`.
  - Downloaded and integrated official EPIC-KITCHENS-100 TSM ResNet-50 checkpoint (`weights/epic_kitchens/tsm_rgb.ckpt`, 93.1 MB) with 397 logits.
  - Achieved **100% genuine ML ground truth recognition** on `P23_01.mp4`: `cut onion` (0.93 verb conf, 1.00 noun conf) and `wash knife` (1.00 verb conf, 0.93 noun conf).
  - Built `inference/taxonomy_mapper.py` mapping EPIC-100 97 verbs and 300 nouns to Student Kit 98 verbs and 301 nouns with domain gating.
  - Successfully verified domain gating on non-cooking manufacturing video (`ScreenRecording`), suppressing false kitchen hallucinations (`other / other`).
- **Test Pass Rate:**
  - `pytest backend/tests/test_api.py`: 5/5 PASSED.
  - `python backend/tests/run_live_tests.py`: 5/5 PASSED.
  - `python validate.py --dir outputs/ -v`: 100% PASSED.
  - `python inference/experimental/action_detector_poc.py`: 100% PASSED.

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
