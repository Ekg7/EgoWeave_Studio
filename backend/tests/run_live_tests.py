#!/usr/bin/env python3
"""
EgoWeave Studio — Full-Stack Backend & Inference Integration Test Suite
Validates backend API routes, SQLite persistence, and Track 4 submission conformity.
"""

import sys
import json
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from backend.app.api.routes.health import health_check
from backend.app.api.routes.videos import get_videos
from backend.app.api.routes.results import get_analysis_result
from backend.app.api.routes.evaluation import get_evaluation_metrics
from validate import validate_single_file, load_supported_classes, load_manifest


def run_tests():
    print("==================================================")
    print(" Running EgoWeave Full-Stack API Integration Tests")
    print("==================================================")

    # 1. Test Health Check endpoint
    health = health_check()
    assert health["status"] == "ok", f"Health status check failed: {health}"
    print(f"  [✓ PASS] System Health Check (status={health['status']}, device={health['device']}, python={health['python_version']})")

    # 2. Test Video Library Listing endpoint
    videos = get_videos()
    assert isinstance(videos, list), "Video library listing must return a list"
    assert len(videos) >= 1, "Expected at least 1 video record in database"
    print(f"  [✓ PASS] Video Library Listing: {len(videos)} video(s) found in repository")

    # 3. Test Video Analysis Result & Interaction Graph endpoint
    p02_res = get_analysis_result("P02_109")
    assert p02_res is not None, "Failed to retrieve P02_109 analysis result"
    assert p02_res.submission is not None, "Missing submission object in P02_109 result"
    assert p02_res.graph is not None, "Missing interaction graph in P02_109 result"
    assert "nodes" in p02_res.graph and "edges" in p02_res.graph, "Malformed graph structure"
    assert p02_res.stats is not None, "Missing summary stats in P02_109 result"
    print(f"  [✓ PASS] Video Result & Graph Query (P02_109: {len(p02_res.graph['nodes'])} graph nodes, {len(p02_res.graph['edges'])} edges)")

    # 4. Test Evaluation Lab & Metrics endpoint
    eval_metrics = get_evaluation_metrics()
    assert "total_score" in eval_metrics, "Missing total_score in evaluation metrics"
    assert "action_coverage" in eval_metrics, "Missing action_coverage in evaluation metrics"
    assert eval_metrics["total_score"] > 0, "Total benchmark score must be > 0"
    print(f"  [✓ PASS] Evaluation Lab Metrics (total_score={eval_metrics['total_score']:.1f}/100, coverage={eval_metrics['action_coverage']})")

    # 5. Test Track 4 Validator Integration
    c_cand = ROOT / "student_kit" / "supported_classes.json"
    supported = load_supported_classes(c_cand if c_cand.exists() else ROOT / "supported_classes.json")
    m_cand = ROOT / "student_kit" / "manifest.csv"
    manifest = load_manifest(m_cand if m_cand.exists() else ROOT / "manifest.csv")
    p_cand = ROOT / "student_kit" / "examples" / "P02_109.json"
    p02_file = p_cand if p_cand.exists() else (ROOT / "outputs" / "P02_109.json" if (ROOT / "outputs" / "P02_109.json").exists() else ROOT / "P02_109.json")
    is_valid, errs, warns = validate_single_file(p02_file, supported, manifest)
    assert is_valid, f"P02_109 validation failed: {errs}"
    print(f"  [✓ PASS] Official Track 4 Validator Integration (P02_109.json validated successfully)")

    print("--------------------------------------------------")
    print(" Summary: 5/5 API integration tests PASSED!")
    print("==================================================")
    return True


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
