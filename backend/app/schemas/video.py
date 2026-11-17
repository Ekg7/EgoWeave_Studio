from pydantic import BaseModel
from typing import Optional, Literal

DatasetType = Literal['epic_kitchens_100', 'fpvsum', 'custom']

class VideoMetadataResponse(BaseModel):
    video_id: str
    filename: str
    duration_sec: float
    width: int
    height: int
    fps: float
    dataset: str
    file_size_mb: float
    status: str
    job_id: str
    created_at: str
    thumbnail_url: Optional[str] = ""
    video_url: str
    highlight_url: Optional[str] = ""
    result_json_url: Optional[str] = ""

class UploadResponse(BaseModel):
    video_id: str
    job_id: str
    message: str

