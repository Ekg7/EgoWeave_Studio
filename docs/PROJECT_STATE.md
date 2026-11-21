# EgoWeave Studio — Project State Specification

**Project:** EgoWeave Studio  
**Competition:** Samsung PRISM XR Hackathon 2026 — Track 4: Action-Aware Video Summarization  
**Team ID:** T07  
**Status:** Fully Operational, Tested & Validated  
**Last Updated:** November 2026  

---

## 1. Executive Summary

EgoWeave Studio is an end-to-end, production-grade AI platform for action-aware egocentric video understanding and intelligent summarization tailored for First-Person XR environments.

The system processes long-form egocentric video input, recognizes fine-grained physical actions with temporal boundaries, estimates video-level activity categories adhering strictly to the official 16 supported classes, constructs a temporal interaction graph depicting causal and shared-object relationships, scores frame importance and semantic novelty, and compiles a highlight summary obeying the official $\le 15\%$ duration budget and $\ge 4.0\text{ s}$ minimum segment constraint.

---

## 2. Core Architecture & Pipeline Components

```
                   +----------------------------------+
                   |       Input Video (.mp4)         |
                   +-----------------+----------------+
                                     |
                                     v
                   +-----------------+----------------+
                   |     VideoLoader & Preprocessor   |
                   | (FFmpeg, Farneback Optical Flow) |
                   +-----------------+----------------+
                                     |
               +---------------------+---------------------+
               |                                           |
               v                                           v
+--------------+---------------+             +-------------+--------------+
|   Visual Feature Backbone    |             |   Temporal Motion Analysis |
| (MobileNetV3Small, ImageNet) |             | (Motion Energy, Novelty)   |
+--------------+---------------+             +-------------+--------------+
               |                                           |
               +---------------------+---------------------+
                                     |
                                     v
                   +-----------------+----------------+
                   |    Multi-Scale Action Engine     |
                   |  (Visual Grounding, Bay. Priors, |
                   |   Temporal NMS, Valley Snapping) |
                   +-----------------+----------------+
                                     |
               +---------------------+---------------------+
               |                                           |
               v                                           v
+--------------+---------------+             +-------------+--------------+
| Category Classifier (16 Cls) |             |  Importance Scoring Engine |
| (Peak & Margin Calibration)  |             | (Action Weight, Visual Nov)|
+--------------+---------------+             +-------------+--------------+
               |                                           |
               |                                           v
               |                             +-------------+--------------+
               |                             | Highlight Optimizer (<=15%)|
               |                             | (Greedy Knapsack, Min 4s)  |
               |                             +-------------+--------------+
               |                                           |
               +---------------------+---------------------+
                                     |
                                     v
                   +-----------------+----------------+
                   |  Temporal Interaction Graph      |
                   | (React Flow Nodes, Object Edges) |
                   +-----------------+----------------+
                                     |
               +---------------------+---------------------+
               |                                           |
               v                                           v
+--------------+---------------+             +-------------+--------------+
| Official Output Serializer   |             | Highlight MP4 Compilation  |
|  (Strict 6-key Track 4 JSON) |             |    (FFmpeg Fast Concat)    |
+------------------------------+             +----------------------------+
```

---

## 3. Verified System Capabilities

1. **Strict 6-Key Official Contract:**
   All exported JSON files conform strictly to the Hackathon Track 4 contract:
   - `team_id` (string: `"T07"`)
   - `video_id` (string matching video stem)
   - `duration_sec` (positive float)
   - `label` (`{ "name": str, "score": float }` in $[0.0, 1.0]$, 16 valid classes)
   - `actions` (array of `{ "segment": [start, end], "verb": str, "noun": str, "score": float }`)
   - `highlights` (array of `{ "segment": [start, end] }`, non-overlapping, sorted)
   - Validated 100% clean with official `validate.py`.

2. **Grounded AI Inference:**
   - Visual object detection using pretrained MobileNetV3Small backbone.
   - Elimination of double-softmax distortion and multi-synset bias.
   - Rejection of fabricated kitchen actions on non-kitchen footage (e.g. manufacturing clips correctly classify as `label: "other"` with generic or empty action sets).
   - Motion valley boundary snapping for natural human action transitions.

3. **Full-Stack Application:**
   - React 18.3 + TypeScript + Tailwind CSS frontend.
   - Interactive React Flow temporal interaction graph.
   - Real-time video player with highlight playback mode.
   - FastAPI asynchronous backend with SQLite persistence and Server-Sent Events (SSE).
   - CLI execution mode via `run.ps1` / `run.sh` / `inference.cli`.
