# EgoWeave Studio — Mission 5 Baseline Technical Audit & Quarantine Report
**Samsung PRISM XR Hackathon 2026 — Track 4**  
*Document Version: 1.0*  
*Audit Date: November 17, 2026*

---

## 1. Executive Summary

This audit establishes the clean, verified baseline of EgoWeave Studio for Mission 5. 
All synthetic classification heads created in Mission 4/4B have been **quarantined from the production inference path** into `weights/synthetic_quarantine/`.
The active production pipeline was traced and independently verified across all software layers:
- **Backend Full-Stack Tests:** 5/5 PASSED (`python backend/tests/run_live_tests.py`).
- **Frontend Production Build:** PASSED in 23.07s (`tsc && vite build`).
- **Official JSON Schema Validator:** 4/4 PASSED (`python validate.py --dir outputs/ -v`).
- **End-to-End CLI Video Inference:** PASSED (`python -m inference.cli` on 120s video in ~19.5s on CPU).

---

## 2. Production Baseline Architecture Trace

The active inference path from raw video MP4 to submission JSON was audited end-to-end:

```
[Input Video MP4]
       │
       ▼
[1. VideoLoader (video_loader.py)]
       │  • Extracts duration, native FPS, frame dimensions via OpenCV VideoCapture
       │  • Resamples frames uniformly at 2.0 FPS, max resolution 360p
       ▼
[2. VideoPreprocessor (preprocessing.py)]
       │  • Computes Farneback dense optical flow between successive frames
       │  • Subtracts median camera motion (ego-motion compensation)
       │  • Calculates Bhattacharyya histogram distance (visual novelty)
       ▼
[3. VisualBackbone (visual_backbone.py)]
       │  • Loads authentic MobileNetV3-Small (weights_mobilenet_v3_small_224_1.0_float.h5)
       │  • Evaluates ImageNet-1K visual probabilities across 1000 classes
       │  • Projects activations to domain concepts (kitchen objects & outdoor sports)
       ▼
[4. ActionRecognizer (action_recognition.py)]
       │  • Evaluates multi-scale temporal windows (2.5s, 5.0s, 8.0s)
       │  • Fuses visual object activations with kinematic flow energy
       │  • Applies Bayesian affordance prior P(verb | noun)
       │  • Temporal NMS (tIoU 0.30) & adjacent segment merging
       ▼
[5. ImportanceScorer (importance_scoring.py)]
       │  • Weighted fusion: 0.35 * motion + 0.45 * action_presence + 0.20 * visual_novelty
       ▼
[6. HighlightOptimizer (highlight_optimizer.py)]
       │  • Constrained dynamic programming / greedy coverage optimization
       │  • Enforces budget <= 15.0% duration, segments >= 4.0s, strictly non-overlapping
       ▼
[7. EventGraphBuilder (event_graph.py)]
       │  • Connects co-occurring and causal actions into React Flow graph representation
       ▼
[8. CategoryClassifier (category_classifier.py)]
       │  • 100% visual feature activation scoring across the 16 supported classes
       ▼
[9. JSONSerializer (serializer.py)]
       │  • Serializes to strict 6-key Samsung PRISM schema:
       │    (team_id, video_id, duration_sec, label, actions, highlights)
```

---

## 3. Quarantine of Synthetic Checkpoints

In strict compliance with Mission 5 guidelines, the synthetic classification heads produced in Mission 4/4B:
- `noun_head_weights.npz` (1,261,185 bytes)
- `verb_head_weights.npz` (1,128,274 bytes)
- `category_head_weights.npz` (495,201 bytes)

have been isolated into:
`weights/synthetic_quarantine/`

### Verification of Quarantine
1. **Zero Production References:** No module in `inference/` or `backend/` imports or loads these `.npz` files for inference.
2. **Quarantine Documentation:** A dedicated `weights/synthetic_quarantine/README.md` documents their provenance, confirming that they were trained on synthetic Gaussian distributions around random anchors and must not be used for production inference.
3. **Training Script Relocation:** `train_noun_head.py`, `train_verb_head.py`, and `train_category_head.py` now explicitly output to `weights/synthetic_quarantine/`.
4. **Clean Production Weights Directory:** The `weights/` root now contains exclusively:
   - `weights/keras_cache/models/weights_mobilenet_v3_small_224_1.0_float.h5` (Authentic ImageNet-1K pretrained weights)
   - `weights/imagenet_class_index.json` (Canonical ImageNet-to-WordNet mapping)

---

## 4. Reproducible Baseline Test Results

All regression tests were executed from the terminal and their outputs verified:

### A. Backend Live Integration Tests
```text
Command: python backend/tests/run_live_tests.py
Exit Code: 0
Output Summary:
  [✓ PASS] System Health Check (status=ok, device=cpu, python=3.13.15)
  [✓ PASS] Video Library Listing: 1 video(s) found in repository
  [✓ PASS] Video Result & Graph Query (P02_109: 3 graph nodes, 2 edges)
  [✓ PASS] Evaluation Lab Metrics (total_score=100.0/100, coverage=1.0)
  [✓ PASS] Official Track 4 Validator Integration (P02_109.json validated successfully)
5/5 API integration tests PASSED.
```

### B. Frontend TypeScript & Vite Production Build
```text
Command: npm run build (in frontend/)
Exit Code: 0
Build Time: 23.07 seconds
Bundled Assets:
  dist/index.html                 1.13 kB
  dist/assets/index-Bm4CPMz3.css 47.38 kB
  dist/assets/index-BAdngkiz.js 520.78 kB
Transformation: 1,668 modules transformed cleanly without TypeScript compilation errors.
```

### C. Official Output Schema Validator
```text
Command: python validate.py --dir outputs/ -v
Exit Code: 0
Output Summary:
  [✓ PASS] P02_109.json                 (Highlight budget: 73.00s / 76.84s - 14.2%)
  [✓ PASS] skiing_03.json               (Highlight budget: 37.00s / 38.70s - 14.3%)
  [✓ PASS] test_120s.json               (Highlight budget: 12.00s / 18.00s - 10.0%)
  [✓ PASS] test_generalization_60s.json (Highlight budget:  6.00s /  9.00s - 10.0%)
4/4 files PASSED validation with zero errors and zero warnings.
```

### D. End-to-End Baseline Inference Benchmark
```text
Command: python -m inference.cli tests/sample_data/test_120s.mp4 outputs/test_120s.json
Exit Code: 0
Wall Clock Time: 19.52 seconds
Processed Video Duration: 120.0 seconds
Real-Time Processing Multiplier: 6.15x faster than real-time on CPU
Output Integrity: Validated strictly against Samsung 6-key schema
```
