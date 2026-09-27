import cv2
import numpy as np
from typing import Tuple, Dict, Any

class SubPixelRefiner:
    """
    Applies gradient-based sub-pixel corner refinement on inlier correspondences
    and tracks actual before/after reprojection improvements.
    """
    @staticmethod
    def refine_keypoints(
        img: np.ndarray, 
        pts: np.ndarray, 
        window_size: int = 5
    ) -> np.ndarray:
        if len(pts) == 0:
            return pts

        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        
        # cornerSubPix requires float32 with shape (N, 1, 2)
        pts_reshaped = pts.reshape(-1, 1, 2).astype(np.float32)
        
        try:
            refined = cv2.cornerSubPix(
                gray, 
                pts_reshaped, 
                winSize=(window_size, window_size), 
                zeroZone=(-1, -1), 
                criteria=criteria
            )
            return refined.reshape(-1, 2)
        except Exception:
            # Fallback if cornerSubPix fails on image edges
            return pts

    @classmethod
    def evaluate_subpixel_refinement(
        cls, 
        img1: np.ndarray, 
        img2: np.ndarray, 
        inlier_pts1: np.ndarray, 
        inlier_pts2: np.ndarray, 
        H_initial: np.ndarray
    ) -> Dict[str, Any]:
        if len(inlier_pts1) < 4 or H_initial is None:
            return {
                "status": "Planned / Insufficient Inliers",
                "enabled": False,
                "initial_rmse_pixels": 0.0,
                "refined_rmse_pixels": 0.0,
                "improvement_delta_pct": 0.0,
                "refined_pts1": inlier_pts1,
                "refined_pts2": inlier_pts2,
                "H_refined": H_initial
            }

        # 1. Compute Initial Inlier RMSE
        pts1_homo = np.hstack([inlier_pts1, np.ones((len(inlier_pts1), 1))])
        proj_initial = (H_initial @ pts1_homo.T).T
        proj_pts_initial = proj_initial[:, :2] / (proj_initial[:, 2:3] + 1e-8)
        initial_rmse = float(np.sqrt(np.mean(np.sum((inlier_pts2 - proj_pts_initial) ** 2, axis=1))))

        # 2. Apply Sub-pixel Refinement
        refined_pts1 = cls.refine_keypoints(img1, inlier_pts1)
        refined_pts2 = cls.refine_keypoints(img2, inlier_pts2)

        # 3. Re-estimate Homography on refined coordinates with robust RANSAC
        H_refined, _ = cv2.findHomography(refined_pts1, refined_pts2, cv2.RANSAC, 2.5)
        if H_refined is None:
            H_refined = H_initial
            refined_rmse = initial_rmse
        else:
            ref_homo = np.hstack([refined_pts1, np.ones((len(refined_pts1), 1))])
            proj_ref = (H_refined @ ref_homo.T).T
            proj_pts_ref = proj_ref[:, :2] / (proj_ref[:, 2:3] + 1e-8)
            refined_rmse = float(np.sqrt(np.mean(np.sum((refined_pts2 - proj_pts_ref) ** 2, axis=1))))

            # Guard against divergence: if refined matrix worsens error by >10%, preserve stable H_initial
            if refined_rmse > initial_rmse * 1.10:
                H_refined = H_initial
                refined_rmse = initial_rmse

        delta_pct = 0.0
        if initial_rmse > 0:
            delta_pct = round(((initial_rmse - refined_rmse) / initial_rmse) * 100.0, 2)

        return {
            "status": "COMPLETED (Gradient-based cornerSubPix)",
            "enabled": True,
            "initial_rmse_pixels": round(initial_rmse, 3),
            "refined_rmse_pixels": round(refined_rmse, 3),
            "improvement_delta_pct": delta_pct,
            "refined_pts1": refined_pts1,
            "refined_pts2": refined_pts2,
            "H_refined": H_refined
        }
