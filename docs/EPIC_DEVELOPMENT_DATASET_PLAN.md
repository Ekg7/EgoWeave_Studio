# EgoWeave Studio — EPIC-KITCHENS Development Dataset Plan & Split Verification

**Project:** EgoWeave Studio  
**Competition:** Samsung PRISM XR Hackathon 2026 — Track 4  
**Date:** November 2026  
**Document Status:** Approved Data Protocol Specification

---

## 1. Problem Statement & Motivation

During the audit of the onion-cutting baseline failure (`P23_01.mp4`), two critical insights were established:
1. **Synthetic Fixture Limitations:** Previous test suites utilized `test_demo.mp4` (a 285 KB synthetic video consisting of a black screen with moving white dots) coupled with handcrafted annotations (`test_demo.json`). While effective for CI pipeline plumbing, it provided zero validation of real-world egocentric computer vision models.
2. **Leakage Risk Mitigation:** To compete fairly and accurately in Track 4, any training or validation video utilized during development must have **absolute zero overlap** with the official hackathon evaluation suite defined in `student_kit/manifest.csv`.

---

## 2. Manifest Split Cross-Check & Zero-Leakage Guarantee

An exhaustive cross-check between `student_kit/manifest.csv` and the official EPIC-KITCHENS-100 splits yielded:

- **Total Videos in Hackathon `manifest.csv`:** 187 videos (138 from EPIC-KITCHENS-100, 49 from FPVSum).
- **Total Videos in Official `EPIC_100_train.csv`:** 495 videos across 45 participants (`P01` to `P37`).
- **Overlap Count:** **0 videos (0.00% overlap)**.
  - Verification: `set(train_df['video_id']).intersection(set(manifest_ids)) == set()`.

This confirms that any video selected from `EPIC_100_train.csv` is completely safe for development, feature calibration, and local evaluation without risking benchmark data leakage.

---

## 3. Selected Development Video Suite (5 Benchmark Videos)

Rather than downloading the full 184 GB dataset, EgoWeave Studio establishes a targeted 5-video benchmark suite covering diverse environments, participants, and target culinary actions (`cut onion`, `wash`, `take knife`, `pour`, `open`):

| Video ID | Participant | Duration (s) | Ground Truth Actions | Target Key Actions Present | File Size (Est.) | Storage Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`P23_01`** | P23 | 91.86s | 14 actions | `cut onion`, `take knife`, `clean knife`, `remove peel`, `turn-off tap`, `close door` | 346.5 MB | **Available Locally** (`backend/storage/uploads/P23_01.mp4`) |
| **`P22_102`**| P22 | 228.9s | 44 actions | `wash vegetable`, `cut food`, `open cupboard`, `put plate`, `turn-on tap` | ~550 MB | Planned Download |
| **`P04_115`**| P04 | 256.8s | 42 actions | `take knife`, `cut food`, `move bowl`, `open fridge` | ~620 MB | Planned Download |
| **`P01_102`**| P01 | 273.1s | 42 actions | `wash dish`, `take knife`, `cut vegetable`, `pour sauce`, `stir pan` | ~680 MB | Planned Download |
| **`P30_110`**| P30 | 256.9s | 38 actions | `take knife`, `cut meat`, `put container`, `clean knife` | ~600 MB | Planned Download |
| **Total** | 5 Participants | **1,107.5s (~18.5 min)** | **180 actions** | Comprehensive culinary action coverage | **~2.8 GB** | Efficient & Portable |

---

## 4. Deep Ground Truth Profile: `P23_01` (Primary Benchmark Video)

The 91.86s video `P23_01.mp4` serves as our immediate gold-standard validation sample. Its 14 ground truth annotations from `EPIC_100_train.csv` are:

```
[01] 00:00:00.00 -> 00:00:06.74 | verb: enter-into (id 67) | noun: kitchen         (id 157) | narr: entering into the kitchen
[02] 00:00:06.32 -> 00:00:13.92 | verb: search-for (id 48) | noun: knife           (id   4) | narr: searching for knife
[03] 00:00:14.41 -> 00:00:14.91 | verb: take       (id  0) | noun: knife           (id   4) | narr: took the knife
[04] 00:00:14.79 -> 00:00:18.80 | verb: clean      (id  2) | noun: knife           (id   4) | narr: cleaning the knife
[05] 00:00:18.71 -> 00:00:19.87 | verb: turn-off   (id  8) | noun: tap             (id   0) | narr: closing the tap
[06] 00:00:24.33 -> 00:00:27.79 | verb: close      (id  4) | noun: door            (id   3) | narr: close the door
[07] 00:00:28.10 -> 00:00:38.09 | verb: cut        (id  7) | noun: onion           (id  16) | narr: cutting the onions
[08] 00:00:35.97 -> 00:00:52.53 | verb: remove-off (id 12) | noun: peel            (id  48) | narr: remove the peel off the onion
[09] 00:00:51.44 -> 00:00:56.59 | verb: remove     (id 12) | noun: peel            (id  48) | narr: remove the unwanted layer
[10] 00:01:00.83 -> 00:01:02.01 | verb: put-into   (id  5) | noun: onion           (id  16) | narr: putting onions into the plate
[11] 00:01:02.11 -> 00:01:13.17 | verb: cut        (id  7) | noun: onion:new       (id  16) | narr: cutting new onion
[12] 00:01:13.21 -> 00:01:18.01 | verb: remove-from (id 12) | noun: onion           (id  16) | narr: remove unwanted layer from the onion
[13] 00:01:18.10 -> 00:01:18.84 | verb: put-into   (id  5) | noun: plate           (id   2) | narr: putting into the plate
[14] 00:01:18.94 -> 00:01:29.28 | verb: remove-from (id 12) | noun: onion           (id  16) | narr: remove unwanted layer from the onion
```

### Key Target Intervals to Test:
- **`cut onion` Segment A:** `28.10s -> 38.09s` (Verb ID: 7 `cut`, Noun ID: 16 `onion`).
- **`cut onion` Segment B:** `62.11s -> 73.17s` (Verb ID: 7 `cut`, Noun ID: 16 `onion`).
- **`clean knife` Segment:** `14.79s -> 18.80s` (Verb ID: 2 `wash/clean`, Noun ID: 4 `knife`).

---

## 5. Summary Evaluation Metrics Protocol

To evaluate inference outputs on real videos with ground truth, we utilize the official protocol:
1. **Action Temporal Intersection-over-Union (tIoU):** Matching candidate segments with ground truth intervals at IoU thresholds $\in \{0.1, 0.3, 0.5\}$.
2. **Mean Average Precision (mAP):** Computing precision-recall across the 98 verbs and 301 nouns.
3. **Highlight F1-Score:** Overlap with ground truth key action segments.
4. **Summary Budget Compliance:** Verification that total highlight duration $\le 15.0\%$ of original runtime, with at least one segment $\ge 4.0\text{s}$.
