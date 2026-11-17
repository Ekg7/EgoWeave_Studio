import cv2
import numpy as np
from typing import List, Tuple, Dict


class VideoPreprocessor:
    def __init__(self):
        pass

    @staticmethod
    def compute_motion_and_novelty(sampled_frames: List[Tuple[float, np.ndarray]]) -> List[Dict[str, float]]:
        """
        Calculates motion energy and visual novelty for each sampled frame.
        Uses Farneback optical flow with camera-motion compensation (affine background subtraction).
        """
        if not sampled_frames:
            return []

        results = []
        prev_gray = None

        for idx, (ts, frame) in enumerate(sampled_frames):
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if prev_gray is None:
                results.append({
                    "timestamp": round(ts, 2),
                    "motion_energy": 0.1,
                    "novelty": 0.5,
                })
                prev_gray = gray
                continue

            # 1. Optical Flow
            flow = cv2.calcOpticalFlowFarneback(
                prev_gray, gray, None,
                pyr_scale=0.5, levels=2, winsize=15,
                iterations=2, poly_n=5, poly_sigma=1.1, flags=0
            )
            mag, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])

            # Camera motion compensation: subtract median flow (dominant ego-camera motion)
            med_x = np.median(flow[..., 0])
            med_y = np.median(flow[..., 1])
            comp_x = flow[..., 0] - med_x
            comp_y = flow[..., 1] - med_y
            comp_mag, _ = cv2.cartToPolar(comp_x, comp_y)

            # Local motion energy (independent hand/object motion)
            motion_score = float(np.mean(comp_mag))

            # 2. Visual Novelty: histogram distance between frames
            hist_prev = cv2.calcHist([prev_gray], [0], None, [32], [0, 256])
            hist_curr = cv2.calcHist([gray], [0], None, [32], [0, 256])
            cv2.normalize(hist_prev, hist_prev)
            cv2.normalize(hist_curr, hist_curr)
            hist_dist = cv2.compareHist(hist_prev, hist_curr, cv2.HISTCMP_BHATTACHARYYA)
            novelty_score = float(hist_dist)

            results.append({
                "timestamp": round(ts, 2),
                "motion_energy": motion_score,
                "novelty": novelty_score,
            })
            prev_gray = gray

        # Normalize metrics to [0, 1]
        motions = [r["motion_energy"] for r in results]
        novelties = [r["novelty"] for r in results]

        max_m = max(motions) if motions and max(motions) > 0 else 1.0
        max_n = max(novelties) if novelties and max(novelties) > 0 else 1.0

        for r in results:
            r["motion_energy"] = round(r["motion_energy"] / max_m, 3)
            r["novelty"] = round(r["novelty"] / max_n, 3)

        return results

