import cv2
import numpy as np
from typing import Tuple, Optional

class OutlierFilter:
    @staticmethod
    def estimate_homography_ransac(
        pts1: np.ndarray, 
        pts2: np.ndarray, 
        ransac_thresh: float = 3.0
    ) -> Tuple[Optional[np.ndarray], np.ndarray, float]:
        """
        Estimates projective Homography matrix using RANSAC.
        Returns: (H, inliers_mask, inlier_ratio)
        """
        if len(pts1) < 4 or len(pts2) < 4:
            return None, np.zeros(len(pts1), dtype=bool), 0.0

        H, mask = cv2.findHomography(
            pts1, 
            pts2, 
            cv2.RANSAC, 
            ransacReprojThreshold=ransac_thresh,
            maxIters=2500,
            confidence=0.995
        )

        if mask is not None:
            mask_bool = mask.ravel().astype(bool)
            inlier_count = int(np.sum(mask_bool))
            inlier_ratio = inlier_count / len(pts1) if len(pts1) > 0 else 0.0
            return H, mask_bool, inlier_ratio
        
        return None, np.zeros(len(pts1), dtype=bool), 0.0
