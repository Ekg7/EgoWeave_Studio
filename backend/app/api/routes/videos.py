import shutil
import uuid
import time
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse
from typing import List

from ...core.config import UPLOAD_DIR
from ...database.db import save_video, get_video, list_videos
from ...schemas.video import VideoMetadataResponse, UploadResponse
from ...services.job_service import start_processing_job
from inference.video_loader import VideoLoader

router = APIRouter()


@router.post("", response_model=UploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    dataset: str = Form("epic_kitchens_100")
):
    if not file.filename.lower().endswith(".mp4"):
        raise HTTPException(status_code=400, detail="Only MP4 videos (.mp4) are supported.")

    # Generate safe ID
    stem = Path(file.filename).stem
    safe_id = "".join(c for c in stem if c.isalnum() or c in ("_", "-"))
    if not safe_id:
        safe_id = f"vid_{uuid.uuid4().hex[:8]}"

    job_id = f"job_{uuid.uuid4().hex[:8]}"
    dest_path = UPLOAD_DIR / f"{safe_id}.mp4"

    # Save to disk
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size_mb = round(dest_path.stat().st_size / (1024 * 1024), 2)

    # Read basic metadata
    try:
        loader = VideoLoader(dest_path)
        meta = loader.metadata
    except Exception as e:
        dest_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Invalid or corrupted MP4 video file: {e}")

    video_record = {
        "video_id": safe_id,
        "filename": file.filename,
        "duration_sec": meta["duration_sec"],
        "width": meta["width"],
        "height": meta["height"],
        "fps": meta["fps"],
        "dataset": dataset,
        "file_size_mb": file_size_mb,
        "file_path": str(dest_path),
        "highlight_path": "",
        "status": "processing",
        "job_id": job_id,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    save_video(video_record)

    # Dispatch async background worker
    start_processing_job(job_id=job_id, video_id=safe_id, video_path=dest_path, dataset=dataset)

    return UploadResponse(
        video_id=safe_id,
        job_id=job_id,
        message="Video uploaded successfully and analysis started."
    )


@router.get("", response_model=List[VideoMetadataResponse])
def get_videos():
    rows = list_videos()
    results = []
    for r in rows:
        results.append(VideoMetadataResponse(
            video_id=r["video_id"],
            filename=r["filename"],
            duration_sec=r["duration_sec"],
            width=r["width"],
            height=r["height"],
            fps=r["fps"],
            dataset=r["dataset"],
            file_size_mb=r["file_size_mb"],
            status=r["status"],
            job_id=r["job_id"],
            created_at=r["created_at"],
            thumbnail_url="",
            video_url=f"/api/v1/videos/{r['video_id']}/stream",
            highlight_url=f"/api/v1/videos/{r['video_id']}/highlight.mp4" if r.get("highlight_path") else "",
            result_json_url=f"/api/v1/videos/{r['video_id']}/result.json"
        ))
    return results


@router.get("/{video_id}", response_model=VideoMetadataResponse)
def get_single_video(video_id: str):
    r = get_video(video_id)
    if not r:
        raise HTTPException(status_code=404, detail=f"Video '{video_id}' not found.")
    return VideoMetadataResponse(
        video_id=r["video_id"],
        filename=r["filename"],
        duration_sec=r["duration_sec"],
        width=r["width"],
        height=r["height"],
        fps=r["fps"],
        dataset=r["dataset"],
        file_size_mb=r["file_size_mb"],
        status=r["status"],
        job_id=r["job_id"],
        created_at=r["created_at"],
        thumbnail_url="",
        video_url=f"/api/v1/videos/{r['video_id']}/stream",
        highlight_url=f"/api/v1/videos/{r['video_id']}/highlight.mp4" if r.get("highlight_path") else "",
        result_json_url=f"/api/v1/videos/{r['video_id']}/result.json"
    )


@router.get("/{video_id}/stream")
def stream_video(video_id: str, request: Request):
    r = get_video(video_id)
    if not r or not Path(r["file_path"]).exists():
        raise HTTPException(status_code=404, detail="Video stream file not found.")
    return FileResponse(r["file_path"], media_type="video/mp4")


@router.get("/{video_id}/highlight.mp4")
def stream_highlight_video(video_id: str):
    r = get_video(video_id)
    if not r or not r.get("highlight_path") or not Path(r["highlight_path"]).exists():
        raise HTTPException(status_code=404, detail="Highlight MP4 not yet compiled.")
    return FileResponse(r["highlight_path"], media_type="video/mp4", filename=f"{video_id}_highlight.mp4")

