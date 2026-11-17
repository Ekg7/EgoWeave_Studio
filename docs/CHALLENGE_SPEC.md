# Samsung PRISM XR Hackathon 2026 — Track 4 Challenge Specification
## Action-Aware Video Summarization for First-Person XR

### 1. Executive Summary & Problem Formulation
In First-Person (Egocentric) Extended Reality (XR), continuous video capture generates millions of high-resolution visual frames. Transmitting or processing all raw frames consumes prohibitive network bandwidth, compute, and memory, and floods downstream multimodal agents with redundant visual tokens.

**Goal:** Transform 2–10 minute egocentric video footage into a compact, action-aware summary (target length $\le 15\%$ of original video duration), along with video-level classification, temporal action boundary localization, and a structured temporal interaction representation.

---

### 2. Official Evaluation Criteria & Scoring Weights (100 Points Total)

| Metric | Weight | Dataset Target | Formal Definition & Requirements |
|---|---|---|---|
| **Action Coverage** | **40%** | EPIC-KITCHENS-100 (`highlights`) | Fraction of unique ground-truth action verb-noun pairs captured within the selected highlight intervals. Soft length penalty applies if highlights exceed $15\%$ of duration. |
| **Action mAP** | **25%** | EPIC-KITCHENS-100 (`actions`) | Mean Average Precision across temporal IoU thresholds $[0.1, 0.2, 0.3, 0.4, 0.5]$ evaluating predicted verb-noun actions and temporal boundaries $[start, end]$. |
| **Highlight F1** | **25%** | FPVSum (`highlights`) | Frame-level F1 score against human-annotated consensus top-15% importance frame masks. |
| **Label Accuracy** | **10%** | FPVSum (`label.name`) | Multi-class classification accuracy for the 14 sport/activity categories (or `other`). |

---

### 3. Submission Contract & Output Schema
The official deliverable must execute as:
```bash
./run.sh <video.mp4> <out.json>
```
and pass:
```bash
python validate.py --dir outputs/
```

#### JSON Output Format
Each video must generate a single `<video_id>.json` file with **exactly** the following 6 top-level keys:
```json
{
  "team_id": "string",
  "video_id": "string",
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

#### Constraints
1. **Highlight Budget:** Total duration of `highlights` $\le 0.15 \times \text{duration\_sec}$.
2. **Segment Duration:** At least one highlight segment must be $\ge 4.0\text{ s}$. Any segment $< 4.0\text{ s}$ is ignored during official scoring.
3. **Highlight Ordering & Overlap:** Highlights must be strictly non-overlapping and chronologically ordered ($start_{i} \ge end_{i-1}$).
4. **Vocabulary Compliance:**
   - 16 Video Labels: `bike, bikepolo, boxing, cooking, horse, jumping, longboarding, motor, parkour, plane, rockclimbing, scuba, skate, ski, surfing, other`.
   - 98 Verbs: e.g., `take, put, wash, open, close, cut, pour, mix...`.
   - 301 Nouns: e.g., `pan, knife, door, plate, cup, spoon, fridge, water...`.
5. **No Invented Fields:** Additional keys (e.g. `confidence`, `events`, `graph`) must NOT appear in the competition JSON. Internal graphs and rich annotations are exposed through EgoWeave Studio's dedicated REST/WebSocket API for interactive XR exploration.

