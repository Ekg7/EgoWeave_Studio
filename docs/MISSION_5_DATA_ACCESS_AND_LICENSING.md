# EgoWeave Studio — Mission 5 Data Access, Licensing & Taxonomy Audit
**Samsung PRISM XR Hackathon 2026 — Track 4**  
*Document Version: 1.0*  
*Audit Date: November 17, 2026*

---

## 1. Official Student Package vs. Real Training Data

The official Samsung PRISM Student Package (`student_package/`) contains:
1. `manifest.csv` (187 rows: 138 EPIC-KITCHENS-100 + 49 FPVSum video IDs and durations).
2. `supported_classes.json` (Taxonomy dictionary: 16 labels, 98 verbs, 301 nouns).
3. `validate.py` (Self-contained schema and budget constraint validator).
4. `TEAM_README.md` (Student guide and execution instructions).
5. `examples/` (`P02_109.json` and `skiing_03.json` formatting templates).

> [!IMPORTANT]
> **No Raw Videos Distributed:** Section 2 of `TEAM_README.md` explicitly states:
> *"Raw video files are NOT distributed by the organizers. Teams must download the source videos directly from their official public repositories using the video IDs in `manifest.csv`."*

---

## 2. Dataset Access, Storage Requirements & Licensing

### A. EPIC-KITCHENS-100 Validation Split (138 Videos)
* **Official URL:** `https://epic-kitchens.github.io/2020`
* **Download Repository:** `https://github.com/epic-kitchens/epic-kitchens-download-scripts`
* **Download Endpoint:** University of Bristol Data Repository (`data.bris.ac.uk`).
* **Total Storage Footprint:** **~184 GB** compressed high-definition MP4 videos.
* **Licensing:** **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**. Permitted for academic research and hackathons, commercial use prohibited.
* **Access Feasibility in Current Environment:**
  - Sandboxed execution environment without external internet download access.
  - 184 GB exceeds reasonable local sandbox storage headroom (204 GB available total).
  - Attempting to download the full dataset inside the sandboxed container is blocked.

### B. FPVSum Annotated Videos (49 Videos)
* **Official URL:** `https://github.com/azuxmioy/fpvsum`
* **Video Hosting:** Public YouTube videos accessed via `yt-dlp`.
* **Video Count in Manifest:** **49 live videos** (out of original 98, as several YouTube links have decayed).
* **Format:** `<Category>_<YouTubeID>` (e.g. `Ski_-Z5a4UQmZLs`, `Bike_...`).
* **Licensing:** YouTube Standard / Research use under academic citation.
* **Access Feasibility:** Sandboxed environment cannot stream or download external YouTube videos via `yt-dlp`.

---

## 3. Taxonomy Reconciliation & Vocabulary Mapping

The competition enforces a standardized vocabulary in `supported_classes.json` (schema version: `prism2026-theme01-v1`).

### A. Video-Level Activity Categories (16 Classes)
```json
[
  "bike", "bikepolo", "boxing", "cooking", "horse", "jumping",
  "longboarding", "motor", "parkour", "plane", "rockclimbing",
  "scuba", "skate", "ski", "surfing", "other"
]
```
* **Origin:** 14 categories from FPVSum + `"cooking"` (EPIC-KITCHENS domain) + `"other"` (fallback class).
* **EPIC-KITCHENS Mapping:** All 138 EPIC-KITCHENS videos map to `"cooking"` with 100% domain certainty.
* **FPVSum Mapping:** Videos map to one of the 14 sports categories or `"other"`.

### B. Action Verbs (98 Classes)
* **Origin:** Top 97 frequent verbs from EPIC-KITCHENS-100 + `"other"`.
* **Top Verbs:** `take`, `put`, `wash`, `open`, `close`, `insert`, `turn-on`, `cut`, `turn-off`, `pour`, `mix`, `move`, `check`, `squeeze`, `remove`, `dry`, `fill`, etc.

### C. Action Nouns (301 Classes)
* **Origin:** Top 300 frequent nouns from EPIC-KITCHENS-100 + `"other"`.
* **Top Nouns:** `tap`, `spoon`, `plate`, `cupboard`, `knife`, `pan`, `lid`, `bowl`, `drawer`, `sponge`, `fridge`, `onion`, `container`, `bottle`, `cloth`, `pot`, `water`, `food`, etc.

### D. Out-of-Vocabulary (OOV) Handling
To prevent validation rejection by `validate.py`:
1. Every candidate prediction is strictly cross-referenced against `supported_classes.json`.
2. Any visual concept that does not match an exact vocabulary token is either mapped via semantic synonymy (e.g., cleaver $\to$ `knife`, refrigerator $\to$ `fridge`, Dutch oven $\to$ `pot`, running shoe $\to$ `skate`) or mapped to `"other"`.
3. Zero out-of-vocabulary terms enter the output JSON.
