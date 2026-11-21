# EgoWeave Studio — Next Session Handoff & Maintenance Guide

**Project:** EgoWeave Studio  
**Competition:** Samsung PRISM XR Hackathon 2026 — Track 4  
**Date:** November 2026  

---

## 1. Project State at Handoff

- **Application Health:** Fully functional, tested, and competition-ready.
- **Repository Cleanliness:** Redundant root files removed; all tools point to canonical `student_kit/` files.
- **AI Engine Quality:**
  - Double-softmax bug resolved.
  - Multi-synset concept bias eliminated.
  - Synthetic heads quarantined.
  - Category classifier supports all 16 classes including `"other"` with peak-to-margin thresholding.
  - Action recognition uses grounded visual evidence and optical flow without fabricated fallbacks.
  - Highlight optimizer enforces $\le 15\%$ budget and $\ge 4.0\text{s}$ segment length rules.
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
