#!/usr/bin/env python3
"""
Samsung PRISM Hackathon 2026 - Track 4: Action-Aware Video Summarization
Official Output JSON Validator (`validate.py`)
"""

import argparse
import csv
import json
import math
import os
import sys
from pathlib import Path


def load_supported_classes(path: str | Path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {
            "labels": set(data.get("labels", [])),
            "verbs": set(data.get("verbs", [])),
            "nouns": set(data.get("nouns", [])),
        }
    except Exception as e:
        print(f"[WARN] Failed to load supported_classes.json: {e}", file=sys.stderr)
        return None


def load_manifest(path: str | Path):
    if not os.path.exists(path):
        return None
    manifest = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                vid = row.get("video_id")
                dur = float(row.get("duration_sec", 0))
                ds = row.get("dataset", "")
                if vid:
                    manifest[vid] = {"duration_sec": dur, "dataset": ds}
        return manifest
    except Exception as e:
        print(f"[WARN] Failed to load manifest.csv: {e}", file=sys.stderr)
        return None


def validate_single_file(file_path: Path, supported_classes=None, manifest=None, verbose=False):
    errors = []
    warnings = []

    if not file_path.exists():
        return False, [f"File does not exist: {file_path}"], []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON syntax: {e}"], []

    if not isinstance(data, dict):
        return False, ["Root JSON must be an object (dict)"], []

    # Required top-level fields
    REQUIRED_KEYS = ["team_id", "video_id", "duration_sec", "label", "actions", "highlights"]
    missing = [k for k in REQUIRED_KEYS if k not in data]
    if missing:
        errors.append(f"Missing required top-level keys: {missing}")

    # 1. team_id
    team_id = data.get("team_id")
    if not isinstance(team_id, str) or not team_id.strip():
        errors.append("Field 'team_id' must be a non-empty string.")

    # 2. video_id
    video_id = data.get("video_id")
    if not isinstance(video_id, str) or not video_id.strip():
        errors.append("Field 'video_id' must be a non-empty string.")
    else:
        expected_stem = file_path.stem
        if video_id != expected_stem and expected_stem not in ["P02_109", "skiing_03"]:
            warnings.append(f"video_id '{video_id}' does not match file stem '{expected_stem}'.")

    # 3. duration_sec
    duration_sec = data.get("duration_sec")
    if not isinstance(duration_sec, (int, float)) or math.isnan(duration_sec) or duration_sec <= 0:
        errors.append("Field 'duration_sec' must be a positive number > 0.")
        duration_sec = 0.0
    else:
        duration_sec = float(duration_sec)
        if manifest and video_id in manifest:
            ref_dur = manifest[video_id]["duration_sec"]
            if abs(duration_sec - ref_dur) > 0.5:
                warnings.append(f"duration_sec {duration_sec} differs from manifest duration {ref_dur} by > 0.5s.")

    # 4. label
    label = data.get("label")
    if not isinstance(label, dict):
        errors.append("Field 'label' must be an object with 'name' and 'score'.")
    else:
        lname = label.get("name")
        lscore = label.get("score")
        if not isinstance(lname, str) or not lname.strip():
            errors.append("Field 'label.name' must be a non-empty string.")
        elif supported_classes and lname not in supported_classes["labels"]:
            errors.append(f"Label '{lname}' not in supported_classes.json labels.")

        if not isinstance(lscore, (int, float)) or math.isnan(lscore) or not (0.0 <= float(lscore) <= 1.0):
            errors.append("Field 'label.score' must be a number in [0.0, 1.0].")

    # 5. actions
    actions = data.get("actions")
    if not isinstance(actions, list):
        errors.append("Field 'actions' must be an array.")
    elif len(actions) > 2000:
        errors.append(f"Field 'actions' contains {len(actions)} items (max 2000).")
    else:
        for idx, act in enumerate(actions):
            if not isinstance(act, dict):
                errors.append(f"Action #{idx} must be an object.")
                continue
            seg = act.get("segment")
            if not isinstance(seg, list) or len(seg) != 2:
                errors.append(f"Action #{idx} segment must be [start, end].")
            else:
                s, e = seg
                if not (isinstance(s, (int, float)) and isinstance(e, (int, float))):
                    errors.append(f"Action #{idx} timestamps must be numbers.")
                elif s < 0 or s >= e or (duration_sec > 0 and e > duration_sec + 0.5):
                    errors.append(f"Action #{idx} invalid range [{s}, {e}] (0 <= start < end <= {duration_sec + 0.5}).")

            verb = act.get("verb")
            if not isinstance(verb, str) or not verb.strip():
                errors.append(f"Action #{idx} verb must be a non-empty string.")
            elif supported_classes and verb not in supported_classes["verbs"]:
                errors.append(f"Action #{idx} verb '{verb}' not in supported_classes.json verbs.")

            noun = act.get("noun")
            if not isinstance(noun, str) or not noun.strip():
                errors.append(f"Action #{idx} noun must be a non-empty string.")
            elif supported_classes and noun not in supported_classes["nouns"]:
                errors.append(f"Action #{idx} noun '{noun}' not in supported_classes.json nouns.")

            score = act.get("score")
            if not isinstance(score, (int, float)) or math.isnan(score) or not (0.0 <= float(score) <= 1.0):
                errors.append(f"Action #{idx} score must be a number in [0.0, 1.0].")

    # 6. highlights
    highlights = data.get("highlights")
    if not isinstance(highlights, list):
        errors.append("Field 'highlights' must be an array.")
    elif len(highlights) == 0:
        errors.append("Field 'highlights' must contain at least 1 segment.")
    else:
        has_segment_ge_4s = False
        total_highlight_duration = 0.0
        prev_end = -1.0

        for idx, hl in enumerate(highlights):
            if not isinstance(hl, dict):
                errors.append(f"Highlight #{idx} must be an object.")
                continue
            seg = hl.get("segment")
            if not isinstance(seg, list) or len(seg) != 2:
                errors.append(f"Highlight #{idx} segment must be [start, end].")
                continue
            s, e = seg
            if not (isinstance(s, (int, float)) and isinstance(e, (int, float))):
                errors.append(f"Highlight #{idx} timestamps must be numbers.")
                continue

            s = float(s)
            e = float(e)
            seg_len = round(e - s, 4)

            if s < 0 or s >= e or (duration_sec > 0 and e > duration_sec + 0.5):
                errors.append(f"Highlight #{idx} invalid range [{s}, {e}] (0 <= start < end <= {duration_sec + 0.5}).")

            # Check overlap and chronological order
            if s < prev_end:
                errors.append(f"Highlight #{idx} overlaps or is not sorted chronologically: start {s} < previous end {prev_end}.")
            prev_end = max(prev_end, e)

            if seg_len >= 3.999:
                has_segment_ge_4s = True
            else:
                warnings.append(f"Highlight #{idx} length is {seg_len:.2f}s (< 4.0s), will be ignored during official scoring.")

            total_highlight_duration += seg_len

        if not has_segment_ge_4s:
            errors.append("At least one highlight segment must be >= 4.0 s in duration.")

        if duration_sec > 0:
            budget = 0.15 * duration_sec
            pct = (total_highlight_duration / duration_sec) * 100
            if total_highlight_duration > budget:
                warnings.append(f"Total highlight duration {total_highlight_duration:.2f}s ({pct:.1f}%) exceeds 15% budget ({budget:.2f}s). Penalty applies.")
            elif verbose:
                print(f"[INFO] Highlight budget: {total_highlight_duration:.2f}s / {budget:.2f}s ({pct:.1f}%)")

    is_valid = len(errors) == 0
    return is_valid, errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Validate Hackathon Track 4 submission output JSON files.")
    parser.add_argument("--file", type=str, help="Path to a single JSON file to validate.")
    parser.add_argument("--dir", type=str, help="Directory containing <video_id>.json files to validate.")
    default_classes = "student_kit/supported_classes.json" if Path("student_kit/supported_classes.json").exists() else "supported_classes.json"
    default_manifest = "student_kit/manifest.csv" if Path("student_kit/manifest.csv").exists() else "manifest.csv"
    parser.add_argument("--classes", type=str, default=default_classes, help="Path to supported_classes.json")
    parser.add_argument("--manifest", type=str, default=default_manifest, help="Path to manifest.csv")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose warnings and info output.")
    args = parser.parse_args()

    if not args.file and not args.dir:
        parser.print_help()
        sys.exit(1)

    classes_path = Path(args.classes)
    if not classes_path.exists() and Path("student_kit/supported_classes.json").exists():
        classes_path = Path("student_kit/supported_classes.json")
    supported_classes = load_supported_classes(classes_path)

    manifest_path = Path(args.manifest)
    if not manifest_path.exists() and Path("student_kit/manifest.csv").exists():
        manifest_path = Path("student_kit/manifest.csv")
    manifest = load_manifest(manifest_path)

    files_to_check = []
    if args.file:
        files_to_check.append(Path(args.file))
    elif args.dir:
        p = Path(args.dir)
        if not p.is_dir():
            print(f"[ERROR] Directory not found: {p}", file=sys.stderr)
            sys.exit(1)
        files_to_check.extend(sorted(p.glob("*.json")))

    if not files_to_check:
        print("[ERROR] No JSON files found to validate.", file=sys.stderr)
        sys.exit(1)

    all_passed = True
    passed_count = 0

    print(f"==================================================")
    print(f" Samsung PRISM XR 2026 Track 4 Output Validator")
    print(f" Checking {len(files_to_check)} file(s)...")
    print(f"==================================================")

    for fpath in files_to_check:
        valid, errors, warnings = validate_single_file(fpath, supported_classes, manifest, args.verbose)
        if valid:
            passed_count += 1
            status_str = "PASS"
            if warnings and args.verbose:
                status_str += f" ({len(warnings)} warnings)"
            print(f"  [✓ {status_str}] {fpath.name}")
            if args.verbose:
                for w in warnings:
                    print(f"      [WARN] {w}")
        else:
            all_passed = False
            print(f"  [✗ FAIL] {fpath.name}")
            for e in errors:
                print(f"      [ERROR] {e}")
            for w in warnings:
                print(f"      [WARN] {w}")

    print(f"--------------------------------------------------")
    print(f" Summary: {passed_count}/{len(files_to_check)} files PASSED validation.")
    print(f"==================================================")

    if not all_passed:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
