import asyncio
import json
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional

from ..database.db import save_job, get_job, save_result, save_video, get_video
from ..core.config import OUTPUT_DIR, HIGHLIGHT_DIR, TEAM_ID
from inference.pipeline import EgoWeavePipeline

# In-memory queue registry for active SSE subscribers
job_listeners: Dict[str, list[asyncio.Queue]] = {}


def register_listener(job_id: str) -> asyncio.Queue:
    q = asyncio.Queue()
    if job_id not in job_listeners:
        job_listeners[job_id] = []
    job_listeners[job_id].append(q)
    return q


def unregister_listener(job_id: str, q: asyncio.Queue):
    if job_id in job_listeners:
        if q in job_listeners[job_id]:
            job_listeners[job_id].remove(q)
        if not job_listeners[job_id]:
            del job_listeners[job_id]


def broadcast_event(job_id: str, data: Dict[str, Any]):
    # Save state to DB
    save_job(
        job_id=job_id,
        video_id=data["video_id"],
        status=data["status"],
        progress=data["progress"],
        current_step=data["current_step"],
        error=data.get("error")
    )

    # Dispatch to SSE listeners
    if job_id in job_listeners:
        msg = json.dumps(data)
        for q in job_listeners[job_id]:
            try:
                q.put_nowait(msg)
            except Exception:
                pass


def run_pipeline_worker(job_id: str, video_id: str, video_path: Path, dataset: str):
    """
    Worker function executed in a dedicated background thread.
    """
    def progress_callback(step: str, pct: int):
        # Always emit "processing" status here; the final "completed" broadcast
        # is sent explicitly after pipeline.process_video() returns successfully,
        # avoiding a duplicate completed event from the callback.
        evt = {
            "job_id": job_id,
            "video_id": video_id,
            "status": "processing",
            "progress": min(pct, 99),
            "current_step": step,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        broadcast_event(job_id, evt)

    try:
        pipeline = EgoWeavePipeline(team_id=TEAM_ID)
        out_json_path = OUTPUT_DIR / f"{video_id}.json"
        out_mp4_path = HIGHLIGHT_DIR / f"{video_id}_highlight.mp4"

        # Execute full pipeline
        analysis_result = pipeline.process_video(
            video_path=video_path,
            output_json_path=out_json_path,
            output_highlight_mp4=out_mp4_path,
            dataset=dataset,
            on_progress=progress_callback
        )

        # Persist full results to SQLite
        save_result(
            video_id=video_id,
            submission=analysis_result["submission"],
            graph=analysis_result["graph"],
            stats=analysis_result["stats"]
        )

        # Update video record with highlight path and status
        video_row = get_video(video_id)
        if video_row:
            video_row["status"] = "completed"
            video_row["highlight_path"] = str(out_mp4_path) if out_mp4_path.exists() else ""
            save_video(video_row)

        evt_done = {
            "job_id": job_id,
            "video_id": video_id,
            "status": "completed",
            "progress": 100,
            "current_step": "Inference and summarization completed.",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        broadcast_event(job_id, evt_done)

    except Exception as e:
        # Mark video record as failed so listing endpoint shows correct status
        video_row = get_video(video_id)
        if video_row:
            video_row["status"] = "failed"
            save_video(video_row)

        evt_err = {
            "job_id": job_id,
            "video_id": video_id,
            "status": "failed",
            "progress": -1,
            "current_step": "Failed during processing",
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        broadcast_event(job_id, evt_err)


def start_processing_job(job_id: str, video_id: str, video_path: Path, dataset: str):
    # Initialize job in DB
    save_job(
        job_id=job_id,
        video_id=video_id,
        status="queued",
        progress=0,
        current_step="Queued for analysis"
    )
    # Spawn background thread
    t = threading.Thread(
        target=run_pipeline_worker,
        args=(job_id, video_id, video_path, dataset),
        daemon=True
    )
    t.start()

