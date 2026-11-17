import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, FileResponse

from ...database.db import get_result, get_video
from ...core.config import OUTPUT_DIR
from ...schemas.result import FullResultResponse, SubmissionJSONSchema
from ...schemas.video import VideoMetadataResponse

router = APIRouter()


@router.get("/{video_id}/result", response_model=FullResultResponse)
def get_analysis_result(video_id: str):
    res = get_result(video_id)
    video = get_video(video_id)
    if not res or not video:
        raise HTTPException(status_code=404, detail=f"Analysis results for '{video_id}' not found.")

    meta_resp = VideoMetadataResponse(
        video_id=video["video_id"],
        filename=video["filename"],
        duration_sec=video["duration_sec"],
        width=video["width"],
        height=video["height"],
        fps=video["fps"],
        dataset=video["dataset"],
        file_size_mb=video["file_size_mb"],
        status=video["status"],
        job_id=video["job_id"],
        created_at=video["created_at"],
        thumbnail_url="",
        video_url=f"/api/v1/videos/{video['video_id']}/stream",
        highlight_url=f"/api/v1/videos/{video['video_id']}/highlight.mp4" if video.get("highlight_path") else "",
        result_json_url=f"/api/v1/videos/{video['video_id']}/result.json"
    )

    return FullResultResponse(
        metadata=meta_resp,
        submission=SubmissionJSONSchema(**res["submission"]),
        graph=res["graph"],
        stats=res["stats"]
    )


@router.get("/{video_id}/result.json")
def download_competition_json(video_id: str):
    json_path = OUTPUT_DIR / f"{video_id}.json"
    if json_path.exists():
        return FileResponse(json_path, media_type="application/json", filename=f"{video_id}.json")

    res = get_result(video_id)
    if not res:
        raise HTTPException(status_code=404, detail=f"No results found for '{video_id}'.")

    return JSONResponse(content=res["submission"], headers={"Content-Disposition": f"attachment; filename={video_id}.json"})

