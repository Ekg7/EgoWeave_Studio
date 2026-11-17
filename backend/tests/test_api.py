import pytest
import os
import json
from pathlib import Path

from backend.app.api.routes.health import health_check
from backend.app.api.routes.videos import get_videos
from backend.app.api.routes.results import get_analysis_result
from backend.app.api.routes.evaluation import get_evaluation_metrics
from backend.app.database.db import init_db
from validate import validate_single_file, load_supported_classes, load_manifest

# Ensure database is initialized
init_db()

def test_health_endpoint():
    data = health_check()
    assert data["status"] == "ok"
    assert "version" in data
    assert "device" in data


def test_list_videos():
    data = get_videos()
    assert isinstance(data, list)
    assert len(data) >= 1
    # Check structure
    vid = data[0]
    assert hasattr(vid, "video_id")
    assert hasattr(vid, "dataset")
    assert hasattr(vid, "status")
    assert any(v.video_id == "P02_109" for v in data)


def test_evaluation_endpoint():
    data = get_evaluation_metrics()
    assert "total_score" in data
    assert "action_coverage" in data
    assert "highlight_f1" in data
    assert "label_accuracy" in data
    assert data["total_score"] >= 0.0


def test_analysis_result_and_graph():
    result = get_analysis_result("P02_109")
    assert result is not None
    assert result.submission is not None
    assert result.graph is not None
    assert "nodes" in result.graph
    assert "edges" in result.graph
    assert len(result.graph["nodes"]) > 0


def test_official_json_validation():
    c_cand = Path("student_kit/supported_classes.json")
    supported_classes = load_supported_classes(c_cand if c_cand.exists() else Path("supported_classes.json"))
    m_cand = Path("student_kit/manifest.csv")
    manifest = load_manifest(m_cand if m_cand.exists() else Path("manifest.csv"))

    output_dir = Path("outputs")
    assert output_dir.exists()

    validated_count = 0
    for sample in ["P02_109.json", "skiing_03.json", "test_120s.json", "test_demo.json"]:
        p = output_dir / sample
        if p.exists():
            valid, errors, _ = validate_single_file(p, supported_classes, manifest)
            assert valid, f"Validation failed for {p}: {errors}"
            validated_count += 1

    assert validated_count >= 2
