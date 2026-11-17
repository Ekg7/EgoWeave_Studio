import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ...database.db import get_job
from ...schemas.job import JobProgressResponse
from ...services.job_service import register_listener, unregister_listener

router = APIRouter()


@router.get("/{job_id}", response_model=JobProgressResponse)
def get_job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return JobProgressResponse(
        job_id=job["job_id"],
        video_id=job["video_id"],
        status=job["status"],
        progress=job["progress"],
        current_step=job["current_step"],
        error=job.get("error"),
        timestamp=job["updated_at"]
    )


@router.get("/{job_id}/events")
async def stream_job_events(job_id: str):
    """
    Server-Sent Events endpoint streaming progress directly to the browser.
    """
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    q = register_listener(job_id)

    async def event_generator():
        # First send current state
        init_evt = {
            "job_id": job["job_id"],
            "video_id": job["video_id"],
            "status": job["status"],
            "progress": job["progress"],
            "current_step": job["current_step"],
            "error": job.get("error"),
            "timestamp": job["updated_at"]
        }
        import json
        yield f"data: {json.dumps(init_evt)}\n\n"

        if job["status"] in ("completed", "failed"):
            unregister_listener(job_id, q)
            return

        try:
            while True:
                msg = await q.get()
                yield f"data: {msg}\n\n"
                data = json.loads(msg)
                if data.get("status") in ("completed", "failed"):
                    break
        except asyncio.CancelledError:
            pass
        finally:
            unregister_listener(job_id, q)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

