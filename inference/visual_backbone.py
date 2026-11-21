import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np
import cv2

ROOT = Path(__file__).resolve().parent.parent
os.environ["KERAS_HOME"] = str(ROOT / "weights" / "keras_cache")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

keras = None


class VisualBackbone:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.model = None
        self.weights_path = ROOT / "weights" / "keras_cache" / "models" / "weights_mobilenet_v3_small_224_1.0_float.h5"
        self._model_loaded = False
        self.concept_indices = self._build_concept_indices()

    def _ensure_model_loaded(self):
        if not self._model_loaded:
            self._load_model()
            self._model_loaded = True

    def _load_model(self):
        global keras
        if keras is None:
            try:
                import keras
            except ImportError:
                keras = None

        if keras is None:
            print("[WARN] Keras not available, visual backbone running in fallback mode.")
            return

        try:
            # Load MobileNetV3Small with cached weights
            self.model = keras.applications.MobileNetV3Small(
                weights=str(self.weights_path) if self.weights_path.exists() else "imagenet",
                include_top=True
            )
        except Exception as e:
            print(f"[WARN] Failed to initialize MobileNetV3: {e}")
            self.model = None

    def _build_concept_indices(self) -> Dict[str, List[int]]:
        """
        Maps supported domain concepts (kitchen objects, tools, outdoor sports) to ImageNet output indices.
        """
        return {
            # Kitchen & Dining Nouns (EPIC-KITCHENS vocabulary)
            "knife": [499],                         # cleaver
            "pan": [567],                           # frying pan
            "pot": [521, 738, 926],                 # crock pot, pot, hot pot
            "fridge": [760],                        # refrigerator
            "plate": [729, 923],                    # plate rack, plate
            "cup": [647, 968],                      # measuring cup, cup
            "spoon": [910],                         # wooden spoon
            "fork": [909],                          # fork
            "bottle": [440, 720, 737, 898, 907],   # water, beer, wine, pop bottle
            "bowl": [659, 809],                     # mixing bowl, soup bowl
            "microwave": [651],                     # microwave
            "dishwasher": [534],                    # dishwasher
            "toaster": [859],                       # toaster
            "oven": [544],                          # Dutch oven
            "tap": [725, 760],                      # faucet / sink context proxy
            "water": [725, 898],                    # pitcher, water bottle
            "onion": [935, 964],                    # vegetable / food proxy
            "vegetable": [935, 964],                # vegetable / mashed potato / potpie proxy
            "meat": [923, 964, 965],                # meat / food plate
            "bread": [923, 931, 964],               # bakery / loaf
            "food": [923, 926, 964],                # general food plate/dish
            "oil": [440, 737, 898],                 # bottle context
            "spatula": [910, 567],                  # cooking tool proxy
            "drawer": [760, 534],                   # cabinet / drawer proxy
            "door": [760, 534],                     # door / cabinet proxy
            "container": [659, 729],                # container proxy
            "box": [478, 659],                     # carton / box

            # Outdoor & Sport Categories (FPVSum classes - exact ImageNet-1k indices)
            "bike": [444, 671],                                 # bicycle-built-for-two, mountain_bike
            "bikepolo": [444, 671],                             # bicycle sports
            "boxing": [242, 747],                               # boxer, punching_bag
            "horse": [339, 603],                                # sorrel, horse_cart
            "jumping": [701],                                   # parachute
            "longboarding": [770, 781],                         # athletic shoe / board proxy
            "motor": [665, 670],                                # moped, motor_scooter
            "parkour": [770, 884],                              # running_shoe, vault
            "plane": [404, 895],                                # airliner, warplane
            "rockclimbing": [500, 672, 970, 972],               # cliff_dwelling, mountain_tent, alp, cliff
            "scuba": [801, 983],                                # snorkel, scuba_diver
            "skate": [770, 781],                                # athletic shoe / scoreboard proxy
            "ski": [795, 796, 802],                             # ski, ski_mask, snowmobile
            "surfing": [814, 842, 975, 977, 978],               # speedboat, swimming_trunks, lakeside, sandbar, seashore
            "cooking": [499, 521, 567, 647, 651, 659, 725, 729, 738, 760, 809, 813, 827, 828, 849, 859, 910, 923, 926, 968], # kitchen aggregate
        }

    def extract_batch_features(self, frames: List[np.ndarray]) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """
        Extracts visual activation vectors for a batch of BGR video frames.
        Returns:
            - logits: Raw probability distribution across 1000 visual classes (N, 1000)
            - concept_scores: Aggregated detection probabilities for canonical domain concepts (Dict[concept -> np.ndarray (N,)])
        """
        self._ensure_model_loaded()

        if not frames or self.model is None:
            # Fallback uniform features if model is absent
            n = len(frames) if frames else 1
            dummy_logits = np.ones((n, 1000), dtype=np.float32) / 1000.0
            dummy_concepts = {c: np.full(n, 0.25, dtype=np.float32) for c in self.concept_indices}
            return dummy_logits, dummy_concepts

        # Preprocess frames: BGR to RGB, resize to 224x224, scale to [-1, 1]
        processed = []
        for f in frames:
            rgb = cv2.cvtColor(f, cv2.COLOR_BGR2RGB)
            resized = cv2.resize(rgb, (224, 224), interpolation=cv2.INTER_LINEAR)
            norm = (resized.astype(np.float32) / 127.5) - 1.0
            processed.append(norm)

        batch_tensor = np.array(processed, dtype=np.float32)

        # Forward pass through MobileNetV3 (already outputs softmax probability distribution across 1000 classes)
        raw_output = self.model(batch_tensor, training=False).numpy()

        # MobileNetV3 with include_top=True has a softmax output layer.
        # Ensure numerical stability and valid probability normalization.
        probs = np.clip(raw_output, 1e-7, 1.0)
        probs = probs / np.sum(probs, axis=-1, keepdims=True)

        # Extract concept-specific scores using max activation across synonymous synsets.
        # Using np.max prevents concepts with multiple synsets (e.g. bottle, cooking)
        # from artificially dominating single-synset concepts.
        concept_scores = {}
        for concept, indices in self.concept_indices.items():
            valid_indices = [idx for idx in indices if idx < probs.shape[1]]
            if valid_indices:
                concept_scores[concept] = np.max(probs[:, valid_indices], axis=1)
            else:
                concept_scores[concept] = np.zeros(len(frames), dtype=np.float32)

        return probs, concept_scores

    def extract_video_features(self, sampled_frames: List[Tuple[float, np.ndarray]]) -> Dict[str, Any]:
        """
        Extracts temporal timestamps, probability distributions, and concept scores for all sampled frames.
        """
        if not sampled_frames:
            return {
                "timestamps": np.array([], dtype=np.float32),
                "probs": np.zeros((0, 1000), dtype=np.float32),
                "concepts": {c: np.array([], dtype=np.float32) for c in self.concept_indices}
            }

        timestamps = np.array([ts for ts, _ in sampled_frames], dtype=np.float32)
        raw_frames = [f for _, f in sampled_frames]
        probs, concept_scores = self.extract_batch_features(raw_frames)

        return {
            "timestamps": timestamps,
            "probs": probs,
            "concepts": concept_scores
        }

