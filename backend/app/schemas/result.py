from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from .video import VideoMetadataResponse

class ActionSchema(BaseModel):
    segment: List[float]
    verb: str
    noun: str
    score: float

class HighlightSchema(BaseModel):
    segment: List[float]

class LabelSchema(BaseModel):
    name: str
    score: float

class SubmissionJSONSchema(BaseModel):
    team_id: str
    video_id: str
    duration_sec: float
    label: LabelSchema
    actions: List[ActionSchema]
    highlights: List[HighlightSchema]

class FullResultResponse(BaseModel):
    metadata: VideoMetadataResponse
    submission: SubmissionJSONSchema
    graph: Dict[str, Any]
    stats: Dict[str, Any]

