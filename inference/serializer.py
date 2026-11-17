import json
from pathlib import Path
from typing import Dict, Any, List


class JSONSerializer:
    def __init__(self, team_id: str = "T07"):
        self.team_id = team_id

    def format_submission_json(
        self,
        video_id: str,
        duration_sec: float,
        label: Dict[str, Any],
        actions: List[Dict[str, Any]],
        highlights: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Formats analysis outputs into the exact 6 required top-level fields for the competition.
        Removes any internal fields (e.g. importance, debug info) from highlights and actions.
        """
        # Clean actions
        clean_actions = []
        for a in actions:
            clean_actions.append({
                "segment": [round(float(a["segment"][0]), 2), round(float(a["segment"][1]), 2)],
                "verb": str(a["verb"]),
                "noun": str(a["noun"]),
                "score": round(float(a["score"]), 2),
            })

        # Clean highlights (official format uses {"segment": [start, end]})
        clean_highlights = []
        for h in highlights:
            clean_highlights.append({
                "segment": [round(float(h["segment"][0]), 2), round(float(h["segment"][1]), 2)]
            })

        output = {
            "team_id": self.team_id,
            "video_id": str(video_id),
            "duration_sec": round(float(duration_sec), 2),
            "label": {
                "name": str(label.get("name", "cooking")),
                "score": round(float(label.get("score", 0.90)), 2),
            },
            "actions": clean_actions,
            "highlights": clean_highlights,
        }
        return output

    def save_json(self, data: Dict[str, Any], output_path: str | Path):
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=1)

