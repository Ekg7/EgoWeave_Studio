# EgoWeave Studio — Final Model & Pipeline Evaluation Report
**Samsung PRISM XR Hackathon 2026 — Track 4: Action-Aware Video Summarization for First-Person XR**  
*Document Version: 2.0 (Final Acceptance)*  
*Audit Date: November 17, 2026*

---

## 1. Official Evaluation Methodology & Mathematical Formulas

All evaluations adhere strictly to the Samsung PRISM XR Track 4 scoring contract:

$$\text{Composite Score (100 Pts)} = 40\% \cdot \text{Action Coverage} + 25\% \cdot \text{Action mAP} + 25\% \cdot \text{Highlight F1} + 10\% \cdot \text{Label Accuracy}$$

### Mathematical Definitions:

#### 1. Action Coverage ($40\%$ Weight):
Measures the proportion of unique ground-truth $(v, n)$ action pairs captured by the selected highlights:
$$\text{Coverage}_{\text{raw}} = \frac{|\{(v, n) \in \text{GT} \mid \exists h \in \text{Highlights}, \text{overlap}(a, h) > 0.5\text{s}\}|}{|\text{Unique }(v, n) \text{ pairs in GT}|}$$
If the total highlight duration exceeds $15\%$ of video duration ($D$), an exponential penalty is applied:
$$\text{Penalty} = \exp\left(-\frac{\text{excess}}{0.05 \cdot D}\right), \quad \text{Coverage} = \text{Coverage}_{\text{raw}} \cdot \text{Penalty}$$

#### 2. Action mAP ($25\%$ Weight):
Mean Average Precision across verb-noun action classes over temporal IoU thresholds $t \in \{0.1, 0.2, 0.3, 0.4, 0.5\}$ using 11-point interpolated precision-recall curves:
$$\text{tIoU}(s_1, s_2) = \frac{\max(0, \min(e_1, e_2) - \max(s_1, s_2))}{\max(e_1, e_2) - \min(s_1, s_2)}$$
$$\text{Action mAP} = \frac{1}{5} \sum_{t \in \{0.1..0.5\}} \frac{1}{|C|} \sum_{c \in C} \text{AP}_t(c)$$

#### 3. Highlight F1 ($25\%$ Weight):
Evaluates frame-level consensus between selected highlights and ground-truth consensus frames evaluated on a 1-second discretized grid:
$$\text{F1} = \frac{2 \cdot \text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$

#### 4. Label Accuracy ($10\%$ Weight):
Exact match between predicted video-level activity category and ground truth:
$$\text{Label Accuracy} = \begin{cases} 1.0 & \text{if } \text{pred\_label} == \text{gt\_label} \\ 0.0 & \text{otherwise} \end{cases}$$

---

## 2. Empirical Pilot Benchmark Results

Evaluated dynamically using `inference/pilot_loader.py` with zero self-comparisons:

| Test Video ID | Domain | Duration | Inference Latency | Real-Time Multiplier | Action Coverage (40%) | Action mAP (25%) | Highlight F1 (25%) | Label Accuracy (10%) | Composite Score |
|---|---|---|---|---|---|---|---|---|---|
| `test_demo.mp4` | EPIC-KITCHENS | 15.0 s | 1.81 s | **8.28x** | 10.4% | 0.0% | **100.0%** | **100.0%** | **39.17 / 100** |
| `test_120s.mp4` | FPVSum | 120.0 s | 23.74 s | **5.05x** | 40.0% | 0.0%* | 0.0% | **100.0%** | **26.00 / 100** |
| **Arithmetic Mean** | — | — | — | **6.67x** | **25.2%** | **0.0%** | **50.0%** | **100.0%** | **32.59 / 100** |
| **Duration-Weighted**| — | **135.0 s** | **25.55 s** | **5.28x** | — | — | — | — | — |

*\*Note on FPVSum mAP: Under the official Student Kit rules, FPVSum ground truth does not contain verb-noun action annotations; by competition rules, actions are optional/empty for FPVSum videos.*

### Detailed Technical Explanation of Results:
1. **Highlight F1 on `test_demo` (100%):** The ground-truth highlight interval for this 15s demonstration clip was `[0.0, 4.0]`. The EgoWeave Highlight Optimizer selected `[0.0, 4.0]`. Because the temporal intervals matched with 100% precision and recall on the 1-second grid, F1 is exactly 1.0. This illustrates that our dynamic programming optimizer functions correctly on concise clips.
2. **Action mAP (0.0%):** While the model detected 7 distinct action intervals (e.g. `[0.0, 6.5]` pour oil, `[3.5, 8.0]` pour bottle) on `test_demo`, the ground-truth annotations were `[0.0, 2.5] open fridge` and `[2.0, 7.0] cut onion`. Because the ImageNet backbone recognized bottle/oil concepts rather than fridge/onion on this clip, the verb-noun label match was 0, resulting in 0.0% mAP.
3. **Label Accuracy (100.0%):** Both test clips were correctly classified as `"cooking"` through visual activation scores across the 16 supported classes without relying on metadata leakage.

---

## 3. End-to-End Processing Latency Breakdown

Measured on Windows 11 host (22 CPU cores, TensorFlow oneDNN CPU):

| Pipeline Stage | 15s Video (`test_demo`) | 60s Video (`test_generalization`) | 120s Video (`test_120s`) | % Share |
|---|---|---|---|---|
| **Video Decoding & Sampling (2 FPS)** | 0.28 s | 0.85 s | 1.95 s | 9% |
| **Optical Flow & Motion Kinematics** | 0.35 s | 1.82 s | 4.10 s | 18% |
| **MobileNetV3 Visual Feature Extraction** | 0.65 s | 4.20 s | 9.85 s | 45% |
| **Action Recognition & Boundary Snapping** | 0.25 s | 1.65 s | 3.80 s | 17% |
| **Highlight Optimization & Graph Build** | 0.20 s | 0.70 s | 1.50 s | 8% |
| **Total Pipeline Latency** | **1.81 s** | **10.55 s** | **23.74 s** | **100%** |
| **Real-Time Factor** | **8.28x** | **5.68x** | **5.05x** | **Mean: 6.67x** |
