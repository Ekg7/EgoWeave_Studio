from pydantic import BaseModel
from typing import Optional

class JobProgressResponse(BaseModel):
    job_id: str
    video_id: str
    status: str
    progress: int
    current_step: str
    error: Optional[str] = None
    timestamp: str

