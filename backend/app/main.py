import os
import json
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .core.config import WORKSPACE_DIR, UPLOAD_DIR, OUTPUT_DIR, HIGHLIGHT_DIR
from .database.db import init_db, list_videos, save_video, save_result, save_job
from .api.routes import videos, jobs, results, evaluation, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database
    init_db()

    # Pre-seed initial reference video P02_109 if database empty
    existing = list_videos()
    if not existing:
        ref_cand = WORKSPACE_DIR / "student_kit" / "examples" / "P02_109.json"
        ref_json_path = ref_cand if ref_cand.exists() else WORKSPACE_DIR / "P02_109.json"
        sample_vid = WORKSPACE_DIR / "tests" / "sample_data" / "test_120s.mp4"
        dest_sample = UPLOAD_DIR / "P02_109.mp4"
        if sample_vid.exists() and not dest_sample.exists():
            import shutil
            shutil.copyfile(sample_vid, dest_sample)

        if ref_json_path.exists():
            with open(ref_json_path, "r", encoding="utf-8") as f:
                ref_sub = json.load(f)
        else:
            ref_sub = {
                "team_id": "T07",
                "video_id": "P02_109",
                "duration_sec": 512.3,
                "label": {"name": "cooking", "score": 0.96},
                "actions": [
                    {"segment": [12.4, 18.9], "verb": "open", "noun": "fridge", "score": 0.82},
                    {"segment": [95.2, 141.6], "verb": "cut", "noun": "onion", "score": 0.88},
                    {"segment": [302.0, 318.5], "verb": "wash", "noun": "knife", "score": 0.71}
                ],
                "highlights": [
                    {"segment": [12.0, 23.0]},
                    {"segment": [96.0, 128.0]},
                    {"segment": [303.0, 317.0]},
                    {"segment": [440.0, 456.0]}
                ]
            }

        # Build initial graph
        from inference.event_graph import EventInteractionGraph
        eg = EventInteractionGraph()
        graph_data = eg.build_graph(ref_sub["actions"], ref_sub["highlights"])

        total_hl_dur = sum(h["segment"][1] - h["segment"][0] for h in ref_sub["highlights"])
        hl_pct = (total_hl_dur / ref_sub["duration_sec"]) * 100

        save_video({
            "video_id": "P02_109",
            "filename": "P02_109.mp4",
            "duration_sec": ref_sub["duration_sec"],
            "width": 1920,
            "height": 1080,
            "fps": 30.0,
            "dataset": "epic_kitchens_100",
            "file_size_mb": 284.5,
            "file_path": str(dest_sample) if dest_sample.exists() else "",
            "highlight_path": "",
            "status": "completed",
            "job_id": "job_init_p02",
            "created_at": "2026-11-16T00:00:00Z"
        })

        save_result(
            video_id="P02_109",
            submission=ref_sub,
            graph=graph_data,
            stats={
                "total_actions_count": len(ref_sub["actions"]),
                "unique_action_pairs_count": eg.get_unique_action_pairs_count(),
                "highlight_duration_sec": round(total_hl_dur, 2),
                "highlight_percentage": round(hl_pct, 2),
                "budget_compliance": hl_pct <= 15.0,
                "max_single_highlight_sec": round(max((h['segment'][1] - h['segment'][0] for h in ref_sub['highlights']), default=0), 2),
                "min_single_highlight_sec": round(min((h['segment'][1] - h['segment'][0] for h in ref_sub['highlights']), default=0), 2),
                "processing_time_sec": 4.82,
            }
        )

        save_job(
            job_id="job_init_p02",
            video_id="P02_109",
            status="completed",
            progress=100,
            current_step="Completed"
        )
    yield


app = FastAPI(
    title="EgoWeave Studio API",
    description="Action-Aware Video Summarization and Temporal Interaction Graph Service — Samsung PRISM XR 2026",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(videos.router, prefix="/api/v1/videos", tags=["Videos"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])
app.include_router(results.router, prefix="/api/v1/videos", tags=["Results"])
app.include_router(evaluation.router, prefix="/api/v1/evaluation", tags=["Evaluation"])
app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])

# Serve frontend build in production
dist_dir = WORKSPACE_DIR / "frontend" / "dist"
if dist_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(dist_dir / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = dist_dir / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(dist_dir / "index.html")
