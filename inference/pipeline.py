import os
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, Callable

from .video_loader import VideoLoader, find_tool
from .visual_backbone import VisualBackbone
from .preprocessing import VideoPreprocessor
from .action_recognition import ActionRecognizer
from .event_graph import EventInteractionGraph
from .importance_scoring import ImportanceScorer
from .highlight_optimizer import HighlightOptimizer
from .category_classifier import CategoryClassifier
from .serializer import JSONSerializer


class EgoWeavePipeline:
    def __init__(self, team_id: str = "T07"):
        self.team_id = team_id
        self.action_recognizer = ActionRecognizer()
        self.event_graph = EventInteractionGraph()
        self.importance_scorer = ImportanceScorer()
        self.highlight_optimizer = HighlightOptimizer()
        self.category_classifier = CategoryClassifier()
        self.serializer = JSONSerializer(team_id=team_id)
        self.ffmpeg_bin = find_tool("ffmpeg")

    def process_video(
        self,
        video_path: str | Path,
        output_json_path: Optional[str | Path] = None,
        output_highlight_mp4: Optional[str | Path] = None,
        dataset: str = "epic_kitchens_100",
        on_progress: Optional[Callable[[str, int], None]] = None
    ) -> Dict[str, Any]:
        """
        Executes end-to-end action-aware video summarization on a single video file.
        Returns comprehensive analysis results including official submission JSON and interaction graph.
        """
        t0 = time.time()
        video_path = Path(video_path).resolve()

        def update(msg: str, pct: int):
            if on_progress:
                on_progress(msg, pct)

        # Step 1: Decode Video & Metadata
        update("Extracting video metadata & temporal boundaries...", 10)
        loader = VideoLoader(video_path)
        meta = loader.metadata
        duration = meta["duration_sec"]

        # Step 2: Adaptive Sampling & Motion Analysis
        update("Sampling frames & estimating optical flow...", 25)
        sampled_frames = list(loader.sample_frames(target_fps=2.0, max_size=360))
        motion_profile = VideoPreprocessor.compute_motion_and_novelty(sampled_frames)

        # Step 3: Deep Visual Feature Extraction
        update("Extracting deep visual representations with MobileNetV3...", 40)
        visual_backbone = VisualBackbone.get_instance()
        video_features = visual_backbone.extract_video_features(sampled_frames)

        # Step 4: Multi-Scale Action Recognition
        update("Detecting fine-grained actions with visual backbone & pair priors...", 55)
        actions = self.action_recognizer.detect_actions(
            motion_profile=motion_profile,
            total_duration=duration,
            sampled_frames=sampled_frames,
            video_features=video_features,
            dataset=dataset
        )

        # Step 5: Importance Scoring
        update("Scoring temporal action importance & deep semantic novelty...", 68)
        importance_timeline = self.importance_scorer.compute_frame_importance(
            motion_profile=motion_profile,
            actions=actions,
            duration_sec=duration,
            video_features=video_features
        )

        # Step 6: Highlight Optimization under <= 15% Budget
        update("Optimizing coverage-aware highlight intervals...", 78)
        raw_highlights = self.highlight_optimizer.optimize_highlights(
            importance_timeline=importance_timeline,
            actions=actions,
            duration_sec=duration
        )

        # Step 7: Temporal Interaction Graph Construction
        update("Constructing temporal interaction graph...", 86)
        graph_data = self.event_graph.build_graph(actions=actions, highlights=raw_highlights)

        # Step 8: Category Classification
        update("Classifying video-level activity label...", 92)
        label_pred = self.category_classifier.predict_category(
            video_id=meta["video_id"],
            filename=meta["filename"],
            sampled_frames=sampled_frames,
            video_features=video_features,
            dataset=dataset
        )

        # Step 9: Official JSON Serialization
        update("Compiling official Track 4 JSON submission...", 96)
        submission = self.serializer.format_submission_json(
            video_id=meta["video_id"],
            duration_sec=duration,
            label=label_pred,
            actions=actions,
            highlights=raw_highlights
        )

        if output_json_path:
            self.serializer.save_json(submission, output_json_path)

        # Step 9: Render Highlight MP4 Video (if requested)
        if output_highlight_mp4 and raw_highlights:
            self._render_highlight_video(video_path, raw_highlights, output_highlight_mp4)

        elapsed = round(time.time() - t0, 2)
        total_hl_dur = sum(h["segment"][1] - h["segment"][0] for h in raw_highlights)
        hl_pct = (total_hl_dur / duration * 100) if duration > 0 else 0.0

        update("Completed analysis successfully", 100)

        return {
            "metadata": {
                **meta,
                "dataset": dataset,
                "file_size_mb": round(video_path.stat().st_size / (1024 * 1024), 2),
                "status": "completed",
                "job_id": f"job-{meta['video_id']}",
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "video_url": f"/api/v1/videos/{meta['video_id']}/stream",
                "highlight_url": f"/api/v1/videos/{meta['video_id']}/highlight.mp4" if output_highlight_mp4 else "",
                "result_json_url": f"/api/v1/videos/{meta['video_id']}/result.json",
            },
            "submission": submission,
            "graph": graph_data,
            "stats": {
                "total_actions_count": len(actions),
                "unique_action_pairs_count": self.event_graph.get_unique_action_pairs_count(),
                "highlight_duration_sec": round(total_hl_dur, 2),
                "highlight_percentage": round(hl_pct, 2),
                "budget_compliance": hl_pct <= 15.0,
                "max_single_highlight_sec": round(max((h['segment'][1] - h['segment'][0] for h in raw_highlights), default=0), 2),
                "min_single_highlight_sec": round(min((h['segment'][1] - h['segment'][0] for h in raw_highlights), default=0), 2),
                "processing_time_sec": elapsed,
            }
        }

    def _render_highlight_video(self, source_path: Path, highlights: list, output_path: str | Path):
        """
        Uses FFmpeg to extract and concatenate the selected highlight intervals from the source footage.
        """
        try:
            output_path = Path(output_path).resolve()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Build filter_complex string for FFmpeg
            filter_parts = []
            concat_parts = []
            for i, hl in enumerate(highlights):
                s, e = hl["segment"]
                filter_parts.append(f"[0:v]trim=start={s}:end={e},setpts=PTS-STARTPTS[v{i}];")
                concat_parts.append(f"[v{i}]")

            concat_str = f"{''.join(filter_parts)}{''.join(concat_parts)}concat=n={len(highlights)}:v=1:a=0[outv]"

            cmd = [
                self.ffmpeg_bin,
                "-y",
                "-i", str(source_path),
                "-filter_complex", concat_str,
                "-map", "[outv]",
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-crf", "28",
                str(output_path)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=45)
        except Exception as e:
            print(f"[WARN] Failed to compile highlight video: {e}")

