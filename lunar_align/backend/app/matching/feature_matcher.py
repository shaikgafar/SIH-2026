import cv2
import numpy as np
from typing import List, Tuple, Dict, Any
from app.preprocessing.phase_congruency import compute_phase_congruency_fast
from app.matching.crater_detector import CraterDetector

class HybridFeatureMatcher:
    @staticmethod
    def match_phase_congruency(
        img1: np.ndarray, 
        img2: np.ndarray, 
        ratio_thresh: float = 0.78
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Illumination- and Sun-Angle Invariant Matching:
        1. Transforms both images into Phase Congruency domain (removes shadows & sun angle).
        2. Detects salient structural keypoints on the invariant phase maps.
        3. Extracts descriptors and matches using Lowe's ratio test.
        Returns: (pts1, pts2, pc1, pc2)
        """
        # Step 1: Compute Phase Congruency maps
        pc1 = compute_phase_congruency_fast(img1)
        pc2 = compute_phase_congruency_fast(img2)

        # Step 2: Keypoint detection on phase congruency maps
        # SIFT / AKAZE on phase maps is invariant to lighting
        try:
            detector = cv2.SIFT_create(nfeatures=2500, contrastThreshold=0.015, edgeThreshold=20)
        except Exception:
            detector = cv2.AKAZE_create()

        kp1, des1 = detector.detectAndCompute(pc1, None)
        kp2, des2 = detector.detectAndCompute(pc2, None)

        if des1 is None or des2 is None or len(kp1) < 4 or len(kp2) < 4:
            return np.array([]), np.array([]), pc1, pc2

        # Step 3: Flann / BF Matcher with Lowe's ratio test
        bf = cv2.BFMatcher(cv2.NORM_L2)
        raw_matches = bf.knnMatch(des1, des2, k=2)

        good_pts1 = []
        good_pts2 = []

        for m_pair in raw_matches:
            if len(m_pair) == 2:
                m, n = m_pair
                if m.distance < max(ratio_thresh, 0.80) * n.distance:
                    good_pts1.append(kp1[m.queryIdx].pt)
                    good_pts2.append(kp2[m.trainIdx].pt)

        return np.float32(good_pts1), np.float32(good_pts2), pc1, pc2

    @staticmethod
    def match_classical_sift(
        img1: np.ndarray, 
        img2: np.ndarray, 
        ratio_thresh: float = 0.75
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Baseline Classical SIFT (demonstrates breakdown under severe sun-angle variation).
        """
        sift = cv2.SIFT_create(nfeatures=1000)
        kp1, des1 = sift.detectAndCompute(img1, None)
        kp2, des2 = sift.detectAndCompute(img2, None)

        if des1 is None or des2 is None:
            return np.array([]), np.array([])

        bf = cv2.BFMatcher()
        raw = bf.knnMatch(des1, des2, k=2)

        good_pts1 = []
        good_pts2 = []
        for m_pair in raw:
            if len(m_pair) == 2:
                m, n = m_pair
                if m.distance < ratio_thresh * n.distance:
                    good_pts1.append(kp1[m.queryIdx].pt)
                    good_pts2.append(kp2[m.trainIdx].pt)

        return np.float32(good_pts1), np.float32(good_pts2)

    @classmethod
    def match_multi_modal_hybrid(
        cls, 
        img1: np.ndarray, 
        img2: np.ndarray, 
        method: str = "HYBRID_PHASE_CONGRUENCY",
        scale_ratio: float = 1.0
    ) -> Dict[str, Any]:
        """
        High-level dispatcher executing the selected matching pipeline.
        """
        pc1, pc2 = None, None

        if method == "CLASSICAL_SIFT":
            pts1, pts2 = cls.match_classical_sift(img1, img2)
        elif method == "GEOMETRIC_CRATER":
            craters1 = CraterDetector.detect_crater_rims(img1)
            craters2 = CraterDetector.detect_crater_rims(img2)
            c_matches = CraterDetector.match_crater_graphs(craters1, craters2, scale_ratio=scale_ratio)
            pts1 = np.float32([m[0] for m in c_matches]) if c_matches else np.array([])
            pts2 = np.float32([m[1] for m in c_matches]) if c_matches else np.array([])
        else: # Default: HYBRID_PHASE_CONGRUENCY
            pts1, pts2, pc1, pc2 = cls.match_phase_congruency(img1, img2)
            # If crater matches exist, augment tie points
            craters1 = CraterDetector.detect_crater_rims(img1)
            craters2 = CraterDetector.detect_crater_rims(img2)
            c_matches = CraterDetector.match_crater_graphs(craters1, craters2, scale_ratio=scale_ratio)
            if c_matches:
                c_pts1 = np.float32([m[0] for m in c_matches])
                c_pts2 = np.float32([m[1] for m in c_matches])
                if len(pts1) > 0:
                    pts1 = np.vstack([pts1, c_pts1])
                    pts2 = np.vstack([pts2, c_pts2])
                else:
                    pts1, pts2 = c_pts1, c_pts2

        return {
            "pts1": pts1,
            "pts2": pts2,
            "pc1": pc1,
            "pc2": pc2
        }
