# EgoWeave Studio — Training & Evaluation Data Audit
**Samsung PRISM XR Hackathon 2026 — Track 4**  
*Document Version: 2.0 (Mission 4B Independent Audit)*  
*Audit Date: November 16, 2026*

---

## 1. Executive Summary

This document establishes the verified inventory and provenance of all data assets present in the EgoWeave Studio workspace. Following the strict rules of Mission 4B, this audit explicitly distinguishes between **evaluation manifests**, **class taxonomies**, **reference format examples**, and **genuine human-annotated training data**.

> [!IMPORTANT]
> **Key Finding:** The official Samsung PRISM Student Package does **not** distribute raw training videos or human action annotation tables. The workspace contains **zero** raw EPIC-KITCHENS-100 or FPVSum training video files. All model training scripts previously developed operated on **synthetic random anchor distributions**, not human-annotated frames. The legitimate operational core of EgoWeave Studio is an ImageNet-1K pretrained MobileNetV3 visual backbone combined with dense optical flow motion dynamics and Bayesian affordance priors.

---

## 2. Exhaustive Resource Classification

Every data asset and file in the project has been inspected and classified according to the 7 formal categories:

| Resource Path | Size | Formal Category | Description & Provenance |
|---|---|---|---|
| `manifest.csv` | 6.2 KB | **4. Evaluation Metadata** | 187 target video IDs (138 EPIC-KITCHENS-100 + 49 FPVSum) with official durations. Contains zero visual frames and zero action annotations. |
| `student_kit/manifest.csv` | 6.2 KB | **4. Evaluation Metadata** | Duplicate of root manifest.csv provided in student package. |
| `supported_classes.json` | 6.0 KB | **5. Taxonomy / Class Mappings** | Canonical vocabulary: 16 video labels, 98 verbs, 301 nouns. Class definitions only; zero training samples. |
| `student_kit/supported_classes.json` | 6.0 KB | **5. Taxonomy / Class Mappings** | Duplicate of root taxonomy file. |
| `P02_109.json` | 682 B | **7. Reference Example** | Single valid reference output for EPIC-KITCHENS-100 (cooking domain, 512.3s). Contains 3 actions, 3 highlights. |
| `student_kit/examples/P02_109.json` | 682 B | **7. Reference Example** | Duplicate of root reference example. |
| `skiing_03.json` | 526 B | **7. Reference Example** | Single valid reference output for FPVSum (skiing domain, 71.8s). Contains 0 actions, 2 highlights. |
| `student_kit/examples/skiing_03.json` | 526 B | **7. Reference Example** | Duplicate of root reference example. |
| `skiing_03_fixed.json` | 570 B | **7. Reference Example** | Verified schema-compliant version with `team_id: "T07"`. |
| `TEAM_README.md` | 9.5 KB | **6. Submission Documentation** | Official student package guide specifying output JSON schema, 15% budget constraints, and evaluation metrics. |
| `student_kit/TEAM_README.md` | 9.5 KB | **6. Submission Documentation** | Duplicate of root student guide. |
| `tests/sample_data/test_demo.mp4` | 292 KB | **3. Validation Data (Synthetic)** | 15.0-second synthetic test video used for unit tests. |
| `tests/sample_data/test_120s.mp4` | 178 KB | **3. Validation Data (Synthetic)** | 120.0-second synthetic benchmark video used for latency profiling. |
| `tests/sample_data/test_generalization_60s.mp4` | 382 KB | **3. Validation Data (Synthetic)** | 60.0-second test video used for end-to-end pipeline verification. |
| `tests/sample_data/test_demo.json` | 1.1 KB | **7. Reference Example** | Target output JSON for test_demo.mp4. |
| `tests/sample_data/test_120s.json` | 10.4 KB | **7. Reference Example** | Target output JSON for test_120s.mp4. |
| `weights/keras_cache/.../weights_mobilenet_v3_small_...h5` | 10.7 MB | **Existing Checkpoint** | Official ImageNet-1K pretrained weights for MobileNetV3-Small (88 layers, 1024-d penultimate features). |
| `weights/noun_head_weights.npz` | 1.26 MB | **Existing Checkpoint (Synthetic)** | 301-class head trained on synthetic Gaussian distributions around random anchors. |
| `weights/verb_head_weights.npz` | 1.13 MB | **Existing Checkpoint (Synthetic)** | 98-class head trained on synthetic Gaussian distributions with heuristic motion offsets. |
| `weights/category_head_weights.npz` | 495 KB | **Existing Checkpoint (Synthetic)** | 16-class head trained on synthetic Gaussian distributions around 16 random anchors. |

---

## 3. Dataset Sourcing & External Availability Analysis

As detailed in `TEAM_README.md` Section 2:
> *"Raw video files are NOT distributed by the organizers. Teams must download the source videos directly from their official public repositories using the video IDs in `manifest.csv`."*

### A. EPIC-KITCHENS-100 Validation Split (138 Videos)
- **Source Endpoint:** University of Bristol (`data.bris.ac.uk`) via `epic-kitchens-download-scripts`.
- **Total Storage Requirement:** Approximately **184 GB**.
- **Local Availability:** **0 GB (0 / 138 videos present).**
- **Environment Status:** Sandboxed execution environment without external internet download capabilities or 184 GB allocated disk space.
- **Feasibility:** Infeasible to download or fine-tune full 3D video backbones on raw 184 GB videos in the local environment.

### B. FPVSum Annotated Videos (49 Videos)
- **Source:** YouTube via `yt-dlp`.
- **Local Availability:** **0 / 49 videos present.**
- **Environment Status:** No external network access.
- **Feasibility:** Infeasible to crawl raw YouTube videos without network access.

---

## 4. Integrity and Compliance Conclusions

1. **Class Vocabulary is NOT Training Data:** `supported_classes.json` defines allowable target strings; it provides no visual examples or bounding boxes.
2. **Manifest is NOT Annotated Data:** `manifest.csv` contains video IDs and durations; it contains no temporal boundaries, verb-noun tags, or highlight labels.
3. **Reference Examples are NOT a Benchmark Set:** `P02_109.json` and `skiing_03.json` are two isolated formatting examples provided by the organizers. Evaluating against them cannot be reported as a full 187-video benchmark.
4. **Honest Architectural Baseline:** EgoWeave Studio's verified strength lies in its **zero-shot neuro-symbolic perception architecture**:
   - Real ImageNet visual feature extraction via MobileNetV3.
   - Real dense optical flow motion kinematics.
   - Domain-specific Bayesian verb-noun co-occurrence priors.
   - Graph-based coverage optimization for highlight selection.
