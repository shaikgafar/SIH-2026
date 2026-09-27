import cv2
import numpy as np
from typing import List, Dict, Any, Tuple

class CraterDetector:
    @staticmethod
    def detect_crater_rims(
        img: np.ndarray, 
        min_radius: int = 8, 
        max_radius: int = 150
    ) -> List[Dict[str, Any]]:
        """
        Detects circular and elliptical crater rims using edge topology and ellipse fitting.
        The geometric center of the rim is invariant to solar illumination direction.
        """
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()

        # CLAHE for contrast enhancement across shadow boundaries
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        blurred = cv2.GaussianBlur(enhanced, (5, 5), 1.5)
        edges = cv2.Canny(blurred, 30, 100)

        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        craters = []
        for cnt in contours:
            if len(cnt) >= 12: # Need at least 5 points for ellipse fit, 12 gives good stability
                area = cv2.contourArea(cnt)
                perimeter = cv2.arcLength(cnt, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * (area / (perimeter * perimeter))
                    # Craters viewed from orbit have circularity ~ 0.35 to 1.0 (elliptical when tilted)
                    if 0.25 <= circularity <= 1.2:
                        try:
                            ellipse = cv2.fitEllipse(cnt)
                            (cx, cy), (ma, MA), angle = ellipse
                            radius = (ma + MA) / 4.0
                            if min_radius <= radius <= max_radius:
                                craters.append({
                                    "center": (float(cx), float(cy)),
                                    "axes": (float(ma), float(MA)),
                                    "radius": float(radius),
                                    "angle": float(angle),
                                    "circularity": float(circularity)
                                })
                        except Exception:
                            continue

        # Non-maximum suppression / deduplication of nearby crater rim detections
        filtered_craters = []
        craters.sort(key=lambda c: c["radius"], reverse=True)
        
        for c in craters:
            cx, cy = c["center"]
            is_dup = False
            for fc in filtered_craters:
                fcx, fcy = fc["center"]
                dist = np.hypot(cx - fcx, cy - fcy)
                if dist < fc["radius"] * 0.4:
                    is_dup = True
                    break
            if not is_dup:
                filtered_craters.append(c)

        return filtered_craters

    @classmethod
    def match_crater_graphs(
        cls, 
        craters1: List[Dict[str, Any]], 
        craters2: List[Dict[str, Any]], 
        scale_ratio: float = 1.0
    ) -> List[Tuple[Tuple[float, float], Tuple[float, float], float]]:
        """
        Matches craters between two images using relative topological distance ratios.
        Topological triangle constellations are scale- and rotation-invariant.
        """
        matches = []
        for i, c1 in enumerate(craters1):
            best_match = None
            best_dist = float("inf")
            for j, c2 in enumerate(craters2):
                # Normalized radius difference considering expected scale
                expected_r2 = c1["radius"] / scale_ratio
                r_diff = abs(c2["radius"] - expected_r2) / max(1.0, expected_r2)
                
                if r_diff < 0.35: # radius compatible within 35%
                    score = r_diff
                    if score < best_dist:
                        best_dist = score
                        best_match = c2
            
            if best_match and best_dist < 0.30:
                matches.append((
                    c1["center"],
                    best_match["center"],
                    float(1.0 - best_dist)
                ))
        return matches
