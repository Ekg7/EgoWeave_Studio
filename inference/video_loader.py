import os
import json
import subprocess
import shutil
import cv2
from pathlib import Path
from typing import Dict, Any, Generator, Tuple
import numpy as np


def find_tool(name: str) -> str:
    # 1. Local tools directory
    local_p = Path(__file__).resolve().parent.parent / "tools" / "ffmpeg" / "bin" / f"{name}.exe"
    if local_p.exists():
        return str(local_p)
    # 2. PATH
    which = shutil.which(name)
    if which:
        return which
    return name


class VideoLoader:
    def __init__(self, video_path: str | Path):
        self.video_path = Path(video_path).resolve()
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video file not found: {self.video_path}")
        self.ffprobe_bin = find_tool("ffprobe")
        self.ffmpeg_bin = find_tool("ffmpeg")
        self.metadata = self._extract_metadata()

    def _extract_metadata(self) -> Dict[str, Any]:
        cap = cv2.VideoCapture(str(self.video_path))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1920
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 1080
        cap.release()

        duration = frame_count / fps if fps > 0 else 0.0

        # Refine with ffprobe if available
        try:
            cmd = [
                self.ffprobe_bin,
                "-v", "error",
                "-show_entries", "format=duration:stream=width,height,r_frame_rate,duration",
                "-of", "json",
                str(self.video_path)
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            if res.returncode == 0:
                data = json.loads(res.stdout)
                fmt_dur = float(data.get("format", {}).get("duration", 0))
                if fmt_dur > 0:
                    duration = fmt_dur
                for stream in data.get("streams", []):
                    if stream.get("width") and stream.get("height"):
                        width = int(stream["width"])
                        height = int(stream["height"])
                    if stream.get("r_frame_rate"):
                        parts = stream["r_frame_rate"].split('/')
                        if len(parts) == 2 and float(parts[1]) > 0:
                            fps = float(parts[0]) / float(parts[1])
        except Exception:
            pass

        return {
            "video_id": self.video_path.stem,
            "filename": self.video_path.name,
            "duration_sec": round(duration, 2),
            "width": width,
            "height": height,
            "fps": round(fps, 2),
            "frame_count": frame_count,
        }

    def sample_frames(self, target_fps: float = 2.0, max_size: int = 360) -> Generator[Tuple[float, np.ndarray], None, None]:
        """
        Samples frames uniformly at target_fps, yielding (timestamp_sec, resized_bgr_frame).
        """
        cap = cv2.VideoCapture(str(self.video_path))
        orig_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        frame_interval = max(1, int(round(orig_fps / target_fps)))

        frame_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx % frame_interval == 0:
                ts = frame_idx / orig_fps
                # Resize for fast CV processing
                h, w = frame.shape[:2]
                scale = max_size / max(h, w)
                if scale < 1.0:
                    frame = cv2.resize(frame, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
                yield ts, frame
            frame_idx += 1
        cap.release()

