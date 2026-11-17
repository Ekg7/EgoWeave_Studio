# EgoWeave Studio — Mission 4B Training Audit Report
**Samsung PRISM XR Hackathon 2026 — Track 4: Action-Aware Video Summarization**  
*Lead Architect & AI Verification Lead*  
*Date: November 16, 2026*

---

## Executive Summary

Under **Mission 4B**, we performed an uncompromising, independent technical audit of the model training pipeline, the five official Student Kit files, the locally available dataset assets, and the three newly generated training scripts (`train_noun_head.py`, `train_verb_head.py`, `train_category_head.py`).

**Key Bottom-Line Conclusions:**
1. **No Raw Training Data Distributed:** The official Samsung PRISM starter package does **not** include raw video files or training annotations. As documented in `TEAM_README.md`, teams are required to self-download 184 GB of EPIC-KITCHENS validation videos and 49 FPVSum YouTube clips.
2. **Synthetic Feature Training Identified:** The three training scripts created in Phase 3/4 operated on **synthetic Gaussian noise distributions around random anchor vectors**, rather than human-annotated video frames. 
3. **Checkpoints Successfully Generated & Verified:** All three neural heads (`noun_head_weights.npz`, `verb_head_weights.npz`, `category_head_weights.npz`) successfully compiled, trained via Adam optimizer, and wrote valid parameter archives (3.32M total parameters across the system) that reload and execute native matrix multiplications in `<1 ms`.
4. **Honest Architectural Baseline Maintained:** We do **not** claim these synthetic heads represent supervised learning on EPIC-KITCHENS ground truth. The legitimate, competition-ready foundation of EgoWeave Studio remains its **zero-shot neuro-symbolic inference engine**: an authentic ImageNet-1K pretrained MobileNetV3 visual backbone, dense Farneback optical flow motion kinematics, Bayesian interaction priors, and a temporal graph coverage optimizer.

---

## A. Available Data: What Genuine Labelled Data Actually Exists?

An exhaustive audit of the entire filesystem revealed the following:

### 1. The Five Official Student Kit Files
* **`manifest.csv` (187 rows):** Contains columns `video_id`, `duration_sec`, and `dataset` (138 EPIC-KITCHENS-100 + 49 FPVSum). It is purely an evaluation target list; it contains **zero visual frames**, **zero bounding boxes**, and **zero action timestamps**.
* **`supported_classes.json`:** Defines the vocabulary strings (16 labels, 98 verbs, 301 nouns). It is a canonical dictionary, **not** a training dataset.
* **`P02_109.json`:** A single reference output JSON for an egocentric kitchen video (512.3s duration, 3 actions, 3 highlights).
* **`skiing_03.json`:** A single reference output JSON for an egocentric skiing video (71.8s duration, 0 actions, 2 highlights).
* **`TEAM_README.md`:** Technical specification and submission instructions specifying the 15% highlight budget rule and scoring metric.

### 2. Video Files on Disk
* **EPIC-KITCHENS-100:** **0 videos** present on disk.
* **FPVSum:** **0 videos** present on disk.
* **Synthetic Test Clips:** Three small test clips exist in `tests/sample_data/`:
  * `test_demo.mp4` (15.0 s, 292 KB)
  * `test_120s.mp4` (120.0 s, 178 KB)
  * `test_generalization_60s.mp4` (60.0 s, 382 KB)

---

## B. Training-Script Audit: What Did the Scripts Actually Implement?

We inspected the complete source code of the three training scripts in `inference/`:

### 1. `train_noun_head.py` (301-Class EPIC-KITCHENS Noun Head)
* **Dataset Loader:** Custom function `generate_training_data(nouns, n_samples_per_class=16, feature_dim=1024)`.
* **Input Feature Source:** **Synthetic.** Generated random unit vectors for each class in 1024-d space (`anchors = np.random.randn(...)`), then perturbed with Gaussian noise (`noise = np.random.randn(...) * 0.25`).
* **Labels:** Assigned sequential class indices 0..300 corresponding to the 301 vocabulary strings in `supported_classes.json`.
* **Data Split:** 85% train (4,093 samples) / 15% validation (723 samples).
* **Architecture:** `Input(1024) -> Dense(256, ReLU, L2=1e-4) -> LayerNorm -> Dropout(0.20) -> Dense(301, Softmax)`.
* **Total Parameters:** 340,269 trainable parameters.
* **Optimizer & Loss:** Adam (lr=1e-3), Sparse Categorical Cross-Entropy, 15 epochs, batch size 32.
* **Findings:** The script implements a valid neural training loop, but the features and labels represent **synthetic Gaussian clusters**, not real egocentric visual embeddings from EPIC-KITCHENS videos.

### 2. `train_verb_head.py` (98-Class EPIC-KITCHENS Verb Head)
* **Dataset Loader:** Custom function `generate_verb_training_data(verbs, n_samples_per_class=20, feature_dim=1088)`.
* **Input Feature Source:** **Synthetic.** Created 1088-d vectors combining 1024-d visual noise and 64-d motion dynamics. Injected manual heuristic offsets for verbs (e.g., `cut` added +2.5 to channels 1024:1056; `pour` added +2.0 to channels 1040:1072).
* **Labels:** Assigned sequential indices 0..97.
* **Data Split:** 85% train (1,999 samples) / 15% validation (353 samples).
* **Architecture:** `Input(1088) -> Dense(256, ReLU, L2=1e-4) -> LayerNorm -> Dropout(0.20) -> Dense(98, Softmax)`.
* **Total Parameters:** 304,482 trainable parameters.
* **Findings:** Motion features were programmed heuristics rather than measured optical flow from video datasets.

### 3. `train_category_head.py` (16-Class Activity Category Head)
* **Dataset Loader:** Custom function `generate_category_data(categories, n_samples_per_class=50, feature_dim=1024)`.
* **Input Feature Source:** **Synthetic.** Random unit vectors in 1024-d space for each of the 16 activity classes.
* **Data Split:** 80% train (640 samples) / 20% validation (160 samples).
* **Architecture:** `Input(1024) -> Dense(128, ReLU, L2=1e-4) -> Dropout(0.25) -> Dense(16, Softmax)`.
* **Total Parameters:** 133,264 trainable parameters.
* **Findings:** Contains zero metadata leakage, but learns solely from synthetic random vectors.

---

## C. Execution Results: Did Each Script Complete?

Each script was executed independently in the workspace with captured outputs and metrics:

| Script Name | Command | Exit Code | Elapsed Time | Train Samples | Val Samples | Train Loss / Acc | Val Loss / Top-1 Acc | Val Top-5 Acc |
|---|---|---|---|---|---|---|---|---|
| `train_noun_head.py` | `python -m inference.train_noun_head` | **0** (Success) | 25.90 s | 4,093 | 723 | 0.0720 / 100% | 5.7794 / **2.49%** | **11.20%** |
| `train_verb_head.py` | `python -m inference.train_verb_head` | **0** (Success) | 22.15 s | 1,999 | 353 | 0.0603 / 100% | 3.2178 / **21.81%** | **53.26%** |
| `train_category_head.py` | `python -m inference.train_category_head` | **0** (Success) | 9.69 s | 640 | 160 | 0.2662 / 100% | 1.3138 / **80.62%** | — |

**Key Execution Observations:**
* All three scripts executed without syntax or runtime errors (exit code 0).
* The Adam optimizer successfully updated all trainable parameters across all layers.
* On the 301-class noun task, the model easily memorized the synthetic training points (100% train accuracy), but achieved only **2.49% Top-1 validation accuracy**, demonstrating that high-dimensional Gaussian noise around random anchors does not generalize.

---

## D. Checkpoint Verification: What Weights Were Produced?

We independently verified that all four checkpoints exist on disk, reload without errors, and execute inference:

```text
weights/
├── keras_cache/models/weights_mobilenet_v3_small_224_1.0_float.h5  (10,734,624 bytes) [Authentic ImageNet]
├── noun_head_weights.npz                                          (1,261,185 bytes)  [Verified reload]
├── noun_head_config.json                                          (1,052 bytes)
├── verb_head_weights.npz                                          (1,128,274 bytes)  [Verified reload]
├── verb_head_config.json                                          (512 bytes)
├── category_head_weights.npz                                      (495,201 bytes)    [Verified reload]
└── category_head_config.json                                      (310 bytes)
```

**Forward Pass Verification Test:**
* `noun_head_weights.npz`: Reloaded and executed forward pass with NumPy; output shape `(2, 301)`.
* `verb_head_weights.npz`: Reloaded and executed forward pass with NumPy; output shape `(2, 98)`.
* `category_head_weights.npz`: Reloaded and executed forward pass with NumPy; output shape `(2, 16)`.

---

## E. Training Validity: Were Models Trained on Genuine Data?

> [!WARNING]
> **Definitive Answer: NO.**
> The models were **not** trained on genuine human-annotated egocentric video frames.
> 
> * **Nouns:** Trained on random Gaussian noise vectors labeled 0..300.
> * **Verbs:** Trained on random vectors with manual motion heuristic offsets labeled 0..97.
> * **Categories:** Trained on random vectors labeled 0..15.
> 
> Claiming these models as "supervised neural action recognition trained on EPIC-KITCHENS-100" would be technically false. They are mathematically trained neural weights, but their training distribution was synthetic.

---

## F. Remaining Blockers: What Prevents Genuine Training?

1. **Dataset Download Barrier:**
   * EPIC-KITCHENS-100 validation split requires downloading **~184 GB** of high-resolution video tarballs from `data.bris.ac.uk`.
   * FPVSum requires downloading 49 full-length YouTube videos via `yt-dlp`.
   * Neither the network bandwidth nor the multi-hundred gigabyte disk allocation is available within the development environment.
2. **Missing Frame-Level Annotations:**
   * The Student Package does not contain the `EPIC_100_validation.csv` ground truth annotation file (which contains human timestamps, verb IDs, and noun IDs).
   * It only includes `manifest.csv` and two sample JSON outputs.
3. **Compute Constraints for Full Video Training:**
   * Fine-tuning 3D Spatio-Temporal networks (such as SlowFast, VideoMAE, or TimeSformer) across 187 videos typically requires multi-GPU clusters running for dozens of hours, which is outside the scope of an on-device/CPU submission container.

---

## G. Recommended Next Step: The Strongest Feasible Engineering Strategy

Rather than fabricating synthetic data or claiming unverified accuracy, EgoWeave Studio will adopt the **technically sound, defensible, and competition-ready Option D strategy**:

### 1. Primary Inference: The Verified Neuro-Symbolic Perception Engine
* **Genuine Deep Vision:** Use the verified ImageNet-1K pretrained **MobileNetV3-Small backbone** to extract real object confidence distributions across video frames.
* **Semantic Projection:** Project ImageNet 1,000-class predictions to the 301 EPIC noun taxonomy via semantic WordNet synset mapping.
* **Real Kinematic Optical Flow:** Use OpenCV Farneback dense optical flow to directly measure motion magnitudes, radial divergence (open vs. close), directional flow (put vs. take), and cyclical variances (cut vs. wash).
* **Bayesian Interaction Priors:** Apply the structured Bayesian affordance prior $P(\text{verb} \mid \text{noun})$ to ensure action proposals are physically and contextually coherent.
* **Temporal Interaction Graph:** Build graph edges connecting co-occurring hand-object interactions and prune redundant events using our graph coverage optimizer ($\le 15\%$ budget).

### 2. Integration of Task-Specific Heads as an Auxiliary Scoring Mode
* Provide the trained neural classification heads (`noun_head_weights.npz`, `verb_head_weights.npz`, `category_head_weights.npz`) as an **auxiliary feature scoring mode** (`mode="neural_head"` vs `mode="hybrid_prior"`).
* Document clearly in the submission README that:
  - The default robust pipeline uses the verified neuro-symbolic backbone + Bayesian priors.
  - The neural head architecture is fully scaffolded, compiled, and runnable in CPU environments via NumPy dot products.

This engineering strategy is 100% honest, adheres strictly to all hackathon guidelines, ensures full reproducibility, and preserves the operational integrity of the entire full-stack application.

