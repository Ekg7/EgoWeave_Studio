#!/usr/bin/env python3
"""
EgoWeave Studio — Genuine-Data Pilot Pipeline & Baseline Evaluation
Evaluates the EgoWeave inference engine against authentic ground-truth action segments
and highlight intervals without data leakage or self-comparison.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

ROOT = Path(__file__).resolve().parent.parent

from inference.pipeline import EgoWeavePipeline
from inference.metrics import (
    compute_action_coverage,
    compute_action_map,
    compute_highlight_f1,
    compute_label_accuracy,
    compute_composite_score
)


class PilotDataLoader:
    """
    Manages loading and validation of real-world or reference pilot video sequences.
    """
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = Path(data_dir) if data_dir else ROOT / "tests" / "sample_data"
        self.reference_dir = ROOT

    def list_available_pilots(self) -> List[Dict[str, Any]]:
        """
        Discovers paired (MP4 video, Ground Truth JSON) test cases in the workspace.
        """
        pilots = []
        
        # 1. Sample data test clips
        for mp4_path in self.data_dir.glob("*.mp4"):
            video_id = mp4_path.stem
            gt_json_path = self.data_dir / f"{video_id}.json"
            if gt_json_path.exists():
                with open(gt_json_path, "r", encoding="utf-8") as f:
                    gt_data = json.load(f)
                pilots.append({
                    "video_id": video_id,
                    "video_path": str(mp4_path),
                    "gt_json_path": str(gt_json_path),
                    "dataset": "epic_kitchens_100" if "demo" in video_id or "p" in video_id.lower() else "fpvsum",
                    "gt_data": gt_data
                })

        return pilots


def run_pilot_evaluation():
    print("==================================================")
    print(" EgoWeave Studio — Mission 5 Genuine Pilot Evaluation")
    print("==================================================")
    
    loader = PilotDataLoader()
    pilots = loader.list_available_pilots()
    print(f"Discovered {len(pilots)} paired pilot video test cases with authentic ground-truth.")

    if not pilots:
        print("[WARN] No paired video/ground-truth files found in tests/sample_data/.")
        return

    pipeline = EgoWeavePipeline()
    results = []

    for idx, pilot in enumerate(pilots, 1):
        vid_id = pilot["video_id"]
        vpath = pilot["video_path"]
        gt = pilot["gt_data"]
        dataset = pilot["dataset"]
        
        print(f"\n--- [{idx}/{len(pilots)}] Evaluating Pilot Video: {vid_id} ({dataset}) ---")
        t0 = time.time()
        
        # Run independent inference pipeline
        res = pipeline.process_video(vpath, dataset=dataset)
        pred = res.get("submission", res)
        elapsed = time.time() - t0
        
        dur = pred["duration_sec"]
        pred_actions = pred.get("actions", [])
        pred_highlights = pred.get("highlights", [])
        pred_label = pred.get("label", {})
        
        gt_actions = gt.get("actions", [])
        gt_highlights = gt.get("highlights", [])
        gt_label = gt.get("label", {})
        
        print(f" Inferred in {elapsed:.2f}s (Speed: {dur/max(0.1, elapsed):.2f}x real-time)")
        print(f" Predicted Actions: {len(pred_actions)}, Ground Truth Actions: {len(gt_actions)}")
        print(f" Predicted Highlights: {len(pred_highlights)}, Ground Truth Highlights: {len(gt_highlights)}")
        print(f" Predicted Label: {pred_label.get('name')} (conf: {pred_label.get('score')}) | GT: {gt_label.get('name')}")
        
        # Compute official competition metrics
        cov = compute_action_coverage(pred_highlights, gt_actions, dur)
        amap = compute_action_map(pred_actions, gt_actions)
        hl_f1 = compute_highlight_f1(pred_highlights, gt_highlights, dur)
        lbl_acc = compute_label_accuracy(pred_label, gt_label)
        total_score = 40.0 * cov + 25.0 * amap + 25.0 * hl_f1 + 10.0 * lbl_acc
        
        print(f" Metrics Breakdown:")
        print(f"   • Action Coverage (40%): {cov * 100:.1f}%")
        print(f"   • Action mAP      (25%): {amap * 100:.1f}%")
        print(f"   • Highlight F1    (25%): {hl_f1 * 100:.1f}%")
        print(f"   • Label Accuracy  (10%): {lbl_acc * 100:.1f}%")
        print(f"   ► Composite Track 4 Score: {total_score:.2f} / 100.0")
        
        results.append({
            "video_id": vid_id,
            "duration_sec": dur,
            "elapsed_sec": elapsed,
            "coverage": cov,
            "action_map": amap,
            "highlight_f1": hl_f1,
            "label_accuracy": lbl_acc,
            "total_score": total_score
        })

    # Summary Table
    print("\n==================================================")
    print(" PILOT EVALUATION SUMMARY")
    print("==================================================")
    print(f"{'Video ID':<15} {'Duration':<10} {'Inference':<10} {'Coverage':<10} {'mAP':<8} {'HL F1':<8} {'Score':<8}")
    print("-" * 72)
    for r in results:
        print(f"{r['video_id']:<15} {r['duration_sec']:<10.1f} {r['elapsed_sec']:<10.2f} {r['coverage']*100:<10.1f} {r['action_map']*100:<8.1f} {r['highlight_f1']*100:<8.1f} {r['total_score']:<8.2f}")
    
    mean_cov = sum(r["coverage"] for r in results) / len(results)
    mean_map = sum(r["action_map"] for r in results) / len(results)
    mean_f1 = sum(r["highlight_f1"] for r in results) / len(results)
    mean_score = sum(r["total_score"] for r in results) / len(results)
    print("-" * 72)
    print(f"{'MEAN':<15} {'—':<10} {'—':<10} {mean_cov*100:<10.1f} {mean_map*100:<8.1f} {mean_f1*100:<8.1f} {mean_score:<8.2f}")
    print("==================================================")


if __name__ == "__main__":
    run_pilot_evaluation()
