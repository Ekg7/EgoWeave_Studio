# EgoWeave Studio — Model Training Provenance & Checkpoint Verification
**Samsung PRISM XR Hackathon 2026 — Track 4**  
*Document Version: 1.0 (Mission 4B Independent Audit)*  
*Audit Date: November 16, 2026*

---

## 1. Provenance Records for All Checkpoints

### Checkpoint 1: MobileNetV3-Small Visual Backbone
* **Model Name:** `MobileNetV3Small_ImageNet1K`
* **Architecture:** MobileNetV3-Small (Depthwise separable convolutions + Squeeze-and-Excitation + Hard-Swish)
* **Backbone:** Standalone visual backbone
* **Training Dataset:** ImageNet-1K (ILSVRC 2012)
* **Annotation Source:** Human-annotated ImageNet bounding boxes and category labels
* **Training Sample Count:** ~1.28 Million images
* **Validation Sample Count:** 50,000 images
* **Class Count:** 1,000 object categories
* **Data Split:** Standard ImageNet train/val split
* **Training Configuration:** Official TensorFlow / Keras release pre-training
* **Checkpoint Location:** `weights/keras_cache/models/weights_mobilenet_v3_small_224_1.0_float.h5`
* **File Size:** 10,734,624 bytes (10.24 MB)
* **SHA-256 Hash:** `0e77484d852a392e2fb35efef6823ec95b5463f25324aa84eeecdc5645e997f7`
* **Verification Status:** **AUTHENTIC DEEP NEURAL NETWORK CHECKPOINT**. Fully verified on disk, loads in Keras with 88 layers, extracts genuine 1024-d visual feature representations at layer `activation_18`.

---

### Checkpoint 2: Task-Specific Noun Head
* **Model Name:** `EgoWeave_NounHead`
* **Architecture:** `Input(1024) -> Dense(256, ReLU, L2=1e-4) -> LayerNorm -> Dropout(0.20) -> Dense(301, Softmax)`
* **Backbone:** Features derived from MobileNetV3-Small (1024-d)
* **Training Dataset:** Synthetic Gaussian cluster generation around 301 random anchor vectors (`np.random.randn`)
* **Annotation Source:** **Synthetic Generator** (`generate_training_data` in `inference/train_noun_head.py`). No human-annotated video frames were used.
* **Training Sample Count:** 4,093 synthetic samples (16 per class prior to 85/15 split)
* **Validation Sample Count:** 723 synthetic samples
* **Class Count:** 301 EPIC-KITCHENS noun vocabulary classes from `supported_classes.json`
* **Data Split:** 85% train / 15% validation (random shuffle split)
* **Training Configuration:** Adam optimizer (lr=1e-3), batch size 32, sparse categorical cross-entropy loss, 15 epochs.
* **Checkpoint Location:** `weights/noun_head_weights.npz` (Config: `weights/noun_head_config.json`)
* **File Size:** 1,261,185 bytes (1.20 MB)
* **SHA-256 Hash:** `d130d352f0229160...`
* **Training Date:** 2026-11-16
* **Measured Validation Metrics:**
  * Top-1 Accuracy: **2.49%**
  * Top-5 Accuracy: **11.20%**
  * Final Validation Loss: **5.7794**
* **Verification Status:** **SYNTHETIC BENCHMARK EXPERIMENT**. Trainable weights exist, reload cleanly, and execute forward passes via NumPy dot products. However, because the data source was synthetic Gaussian noise rather than human-annotated video frames, this checkpoint **cannot** be claimed as a genuine supervised EPIC-KITCHENS model.

---

### Checkpoint 3: Task-Specific Verb Head
* **Model Name:** `EgoWeave_VerbHead`
* **Architecture:** `Input(1088) -> Dense(256, ReLU, L2=1e-4) -> LayerNorm -> Dropout(0.20) -> Dense(98, Softmax)`
* **Backbone:** 1024-d visual features fused with 64-d optical flow kinematics
* **Training Dataset:** Synthetic feature generation with heuristic kinematic offsets for dynamic verbs
* **Annotation Source:** **Synthetic Generator** (`generate_verb_training_data` in `inference/train_verb_head.py`). No human-annotated video frames were used.
* **Training Sample Count:** 1,999 synthetic samples (20 per class prior to 85/15 split)
* **Validation Sample Count:** 353 synthetic samples
* **Class Count:** 98 EPIC-KITCHENS verb vocabulary classes from `supported_classes.json`
* **Data Split:** 85% train / 15% validation
* **Training Configuration:** Adam optimizer (lr=1e-3), batch size 32, sparse categorical cross-entropy, 15 epochs.
* **Checkpoint Location:** `weights/verb_head_weights.npz` (Config: `weights/verb_head_config.json`)
* **File Size:** 1,128,274 bytes (1.08 MB)
* **SHA-256 Hash:** `eafb5ac85d9ee99b...`
* **Training Date:** 2026-11-16
* **Measured Validation Metrics:**
  * Top-1 Accuracy: **21.81%**
  * Top-5 Accuracy: **53.26%**
  * Final Validation Loss: **3.2178**
* **Verification Status:** **SYNTHETIC BENCHMARK EXPERIMENT**. Trainable weights exist, reload cleanly, and execute forward passes. However, because the motion offsets and feature vectors were generated synthetically, this checkpoint **cannot** be claimed as a genuine supervised EPIC-KITCHENS model.

---

### Checkpoint 4: 16-Class Activity Category Head
* **Model Name:** `EgoWeave_CategoryHead`
* **Architecture:** `Input(1024) -> Dense(128, ReLU, L2=1e-4) -> Dropout(0.25) -> Dense(16, Softmax)`
* **Backbone:** 1024-d pooled visual embeddings from MobileNetV3-Small
* **Training Dataset:** Synthetic visual embedding generation across 16 classes
* **Annotation Source:** **Synthetic Generator** (`generate_category_data` in `inference/train_category_head.py`). No human-annotated FPVSum video frames were used.
* **Training Sample Count:** 640 synthetic samples (50 per class prior to 80/20 split)
* **Validation Sample Count:** 160 synthetic samples
* **Class Count:** 16 official activity classes (`bike`, `cooking`, `ski`, `other`, etc.)
* **Data Split:** 80% train / 20% validation
* **Training Configuration:** Adam optimizer (lr=1e-3), batch size 32, sparse categorical cross-entropy, 20 epochs.
* **Checkpoint Location:** `weights/category_head_weights.npz` (Config: `weights/category_head_config.json`)
* **File Size:** 495,201 bytes (483.6 KB)
* **SHA-256 Hash:** `c56432c8eac5d651...`
* **Training Date:** 2026-11-16
* **Measured Validation Metrics:**
  * Accuracy: **80.62%** (on synthetic distribution)
  * Macro F1: **0.7952**
  * Final Validation Loss: **1.3138**
* **Verification Status:** **SYNTHETIC EXPERIMENT**. Trainable weights exist, reload cleanly, and execute forward passes. However, because only 2 real reference examples (`P02_109.json` for cooking, `skiing_03.json` for skiing) exist in the kit, a full 16-class classifier cannot be legitimately claimed as trained on real FPVSum video data.

---

## 2. Summary of Trainable Parameters and Footprint

| Component | Checkpoint File | Format | Params | File Size | Execution Medium |
|---|---|---|---|---|---|
| **MobileNetV3 Visual Backbone** | `weights_mobilenet_v3_small_...h5` | Keras HDF5 | 2,542,856 | 10.24 MB | Keras / TF (CPU) |
| **Noun Head** | `noun_head_weights.npz` | NumPy Archive | 340,269 | 1.20 MB | NumPy Dot-Product (<1ms) |
| **Verb Head** | `verb_head_weights.npz` | NumPy Archive | 304,482 | 1.08 MB | NumPy Dot-Product (<1ms) |
| **Category Head** | `category_head_weights.npz` | NumPy Archive | 133,264 | 483.6 KB | NumPy Dot-Product (<1ms) |
| **Total System Parameters** | — | — | **3,320,871** | **13.00 MB** | Full Multi-Stage Pipeline |

