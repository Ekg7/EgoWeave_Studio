#!/usr/bin/env python3
"""
Official Hackathon Track 4 Single-Video CLI Runner
Invoked by: ./run.sh <video.mp4> <out.json>
"""

import sys
import os
import csv
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from inference.pipeline import EgoWeavePipeline


def detect_dataset_from_manifest(video_id: str, manifest_path: Path) -> str:
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("video_id") == video_id:
                        return row.get("dataset", "epic_kitchens_100")
        except Exception:
            pass

    # Heuristic fallback
    if (video_id.startswith("P") and "_" in video_id) or "demo" in video_id.lower():
        return "epic_kitchens_100"
    return "fpvsum"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="EgoWeave Studio Track 4 Single-Video CLI Runner")
    parser.add_argument("video_path", type=str, help="Path to input .mp4 video")
    parser.add_argument("output_json", type=str, help="Path to output submission JSON")
    parser.add_argument("--dataset", type=str, default=None, choices=["epic_kitchens_100", "fpvsum"], help="Explicit dataset override")

    args = parser.parse_args()

    video_path = Path(args.video_path).resolve()
    out_json = Path(args.output_json).resolve()

    if not video_path.exists():
        print(f"[ERROR] Input video not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    video_id = video_path.stem
    manifest_cand = ROOT / "student_kit" / "manifest.csv"
    manifest_path = manifest_cand if manifest_cand.exists() else ROOT / "manifest.csv"
    dataset = args.dataset if args.dataset else detect_dataset_from_manifest(video_id, manifest_path)

    print(f"==================================================")
    print(f" EgoWeave Studio — Track 4 Inference Engine")
    print(f" Target Video : {video_path.name} (id: {video_id})")
    print(f" Dataset Type : {dataset}")
    print(f" Output JSON  : {out_json}")
    print(f"==================================================")

    pipeline = EgoWeavePipeline(team_id="T07")

    def progress_callback(step: str, pct: int):
        print(f" [{pct:3d}%] {step}")

    try:
        res = pipeline.process_video(
            video_path=video_path,
            output_json_path=out_json,
            dataset=dataset,
            on_progress=progress_callback
        )
        print(f"--------------------------------------------------")
        print(f" [SUCCESS] Processing complete!")
        print(f" Duration        : {res['metadata']['duration_sec']}s")
        print(f" Actions detected: {len(res['submission']['actions'])}")
        print(f" Highlight budget: {res['stats']['highlight_duration_sec']}s ({res['stats']['highlight_percentage']}%)")
        print(f" Output saved to : {out_json}")
        print(f"==================================================")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] Inference failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

