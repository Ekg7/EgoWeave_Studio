"""
Taxonomy Mapper: Maps EPIC-KITCHENS-100 classes to Student Kit (Samsung XR Track 4) taxonomy.

Background:
- EPIC-KITCHENS-100: 97 verbs (0-96), 300 nouns (0-299).
- Student Kit: 98 verbs (0-96 identical to EPIC, 97 is 'other'),
               301 nouns (0-299 identical to EPIC, 300 is 'other').

This module guarantees strict adherence to the competition schema while allowing
pretrained EPIC-KITCHENS models to map seamlessly to Student Kit format.
"""

import json
import os
from typing import Dict, List, Optional, Tuple

STUDENT_KIT_CLASSES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "student_kit",
    "supported_classes.json"
)

EPIC_VERB_CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data", "annotations", "epic_kitchens", "EPIC_100_verb_classes.csv"
)

EPIC_NOUN_CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data", "annotations", "epic_kitchens", "EPIC_100_noun_classes.csv"
)


class TaxonomyMapper:
    """Handles mapping between EPIC-KITCHENS-100 model outputs and Student Kit taxonomy."""

    def __init__(self, supported_classes_path: Optional[str] = None):
        path = supported_classes_path or STUDENT_KIT_CLASSES_PATH
        if not os.path.exists(path):
            raise FileNotFoundError(f"Supported classes file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.verbs: List[str] = data.get("verbs", [])
        self.nouns: List[str] = data.get("nouns", [])
        self.labels: List[str] = data.get("labels", ["cooking", "skiing", "other"])

        self.verb_to_id: Dict[str, int] = {v: i for i, v in enumerate(self.verbs)}
        self.noun_to_id: Dict[str, int] = {n: i for i, n in enumerate(self.nouns)}
        self.label_to_id: Dict[str, int] = {l: i for i, l in enumerate(self.labels)}

        self.num_verbs = len(self.verbs)  # 98
        self.num_nouns = len(self.nouns)  # 301
        self.other_verb_id = self.verb_to_id.get("other", 97)
        self.other_noun_id = self.noun_to_id.get("other", 300)

        # Sanity check
        assert self.num_verbs == 98, f"Expected 98 verbs, found {self.num_verbs}"
        assert self.num_nouns == 301, f"Expected 301 nouns, found {self.num_nouns}"
        assert self.verbs[-1] == "other", f"Last verb must be 'other', got {self.verbs[-1]}"
        assert self.nouns[-1] == "other", f"Last noun must be 'other', got {self.nouns[-1]}"

    def map_epic_verb(self, epic_verb_id: int, confidence: float, threshold: float = 0.05) -> Tuple[int, str]:
        """
        Map EPIC-100 verb ID (0-96) to Student Kit verb.
        If below threshold or invalid ID, returns ('other', 97).
        """
        if confidence < threshold or epic_verb_id < 0 or epic_verb_id >= 97:
            return self.other_verb_id, "other"
        return epic_verb_id, self.verbs[epic_verb_id]

    def map_epic_noun(self, epic_noun_id: int, confidence: float, threshold: float = 0.05) -> Tuple[int, str]:
        """
        Map EPIC-100 noun ID (0-299) to Student Kit noun.
        If below threshold or invalid ID, returns ('other', 300).
        """
        if confidence < threshold or epic_noun_id < 0 or epic_noun_id >= 300:
            return self.other_noun_id, "other"
        return epic_noun_id, self.nouns[epic_noun_id]

    def map_action(
        self,
        epic_verb_id: int,
        verb_conf: float,
        epic_noun_id: int,
        noun_conf: float,
        category: str = "cooking",
        verb_threshold: float = 0.05,
        noun_threshold: float = 0.05
    ) -> Dict[str, any]:
        """
        Full action mapping with category awareness.
        If category is not cooking (e.g. skiing or other), kitchen actions should default to other/other.
        """
        if category.lower() != "cooking":
            return {
                "verb": "other",
                "verb_id": self.other_verb_id,
                "verb_conf": verb_conf,
                "noun": "other",
                "noun_id": self.other_noun_id,
                "noun_conf": noun_conf,
                "action_str": "other / other"
            }

        v_id, v_str = self.map_epic_verb(epic_verb_id, verb_conf, verb_threshold)
        n_id, n_str = self.map_epic_noun(epic_noun_id, noun_conf, noun_threshold)

        return {
            "verb": v_str,
            "verb_id": v_id,
            "verb_conf": verb_conf,
            "noun": n_str,
            "noun_id": n_id,
            "noun_conf": noun_conf,
            "action_str": f"{v_str} / {n_str}"
        }

    def validate_action(self, verb: str, noun: str) -> bool:
        """Check if verb and noun are valid Student Kit classes."""
        return (verb in self.verb_to_id) and (noun in self.noun_to_id)

    def get_verb_name(self, verb_id: int) -> str:
        if 0 <= verb_id < self.num_verbs:
            return self.verbs[verb_id]
        return "other"

    def get_noun_name(self, noun_id: int) -> str:
        if 0 <= noun_id < self.num_nouns:
            return self.nouns[noun_id]
        return "other"
