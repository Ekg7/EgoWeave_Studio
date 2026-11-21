# EgoWeave Studio — Temporal Interaction Graph & Summarization

**Project:** EgoWeave Studio  
**Competition:** Samsung PRISM XR Hackathon 2026 — Track 4  
**Date:** November 2026  

---

## 1. Temporal Interaction Graph Architecture

The Temporal Interaction Graph models egocentric activities not as isolated time intervals, but as an interconnected network of physical interactions across time.

### 1.1 Node Representation
Each recognized action interval is mapped to a graph node:
- `id`: Unique identifier (e.g., `act_0`, `act_1`).
- `data`:
  - `verb`: Action predicate (e.g. `cut`, `wash`, `take`, `other`).
  - `noun`: Object operand (e.g. `knife`, `pan`, `plate`, `other`).
  - `start`, `end`: Temporal boundaries in seconds.
  - `score`: Confidence score $[0.50, 0.95]$.
  - `isHighlight`: Boolean indicating whether this action is captured in the final highlight summary.
- `position`: Dynamically laid out along the horizontal temporal axis ($x = \text{start} \times 80\text{px}$) with alternating vertical offsets ($y$) to prevent visual clutter in the React Flow viewport.

### 1.2 Edge Relationships
Two classes of directed semantic relationships are established between nodes:
1. **Shared Object Continuity (`shared_noun`):**
   - Connects action $A_i$ to action $A_j$ ($i < j$) if both manipulate the same physical entity ($\text{noun}_i = \text{noun}_j$).
   - Rendered in cyan (`#38bdf8`) with animated flow particles, highlighting the object's lifecycle through the task (e.g., `take knife` $\to$ `cut onion` $\to$ `put knife`).
2. **Temporal Succession (`temporal_sequence`):**
   - Connects adjacent chronological actions within a task transition window ($\Delta t \le 4.0\text{ s}$).
   - Rendered as dashed slate connectors (`#64748b`) labeled `"then"`.

---

## 2. Highlight Optimization Engine

The highlight optimization engine solves a constrained knapsack problem to maximize Action Coverage while respecting all official constraints.

### 2.1 Optimization Objective
Maximize:
$$\mathcal{J}(H) = \sum_{A_i \in \text{Actions}} \mathbb{I}\left(\frac{|A_i \cap H|}{|A_i|} \ge 0.50\right) + \lambda \sum_{h \in H} \bar{I}(h)$$
Subject to:
1. $\sum_{h \in H} (e_h - s_h) \le 0.15 \times \text{duration\_sec}$ (Duration Budget)
2. $\exists h \in H \text{ s.t. } (e_h - s_h) \ge 4.0\text{ s}$ (Minimum Segment Constraint)
3. $s_{h+1} \ge e_h$ (Non-overlapping, chronologically ordered)

### 2.2 Short Video (< 26.67 s) Mathematical Resolution
For videos shorter than $26.67\text{ s}$, a mathematical conflict exists between $\le 15\%$ budget and $\ge 4.0\text{ s}$ segment length ($0.15 \times 26.67 = 4.0$).
Per official validator rules (`validate.py`):
- Failing $\ge 4.0\text{ s}$ is a **FATAL ERROR** (submission invalid).
- Exceeding $15.0\%$ budget on ultra-short videos triggers an advisory warning without invalidation.
- The optimizer prioritizes the hard $\ge 4.0\text{ s}$ requirement by extracting a single optimal $4.0\text{ s}$ segment centered on the peak action, ensuring full compliance.
