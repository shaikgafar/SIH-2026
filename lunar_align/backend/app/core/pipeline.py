import time
import numpy as np
import cv2
from typing import Dict, Any, Optional, List

from app.core.synthetic_lunar import get_prebuilt_lunar_datasets
from app.preprocessing.pyramid import ScalePyramid
from app.matching.feature_matcher import HybridFeatureMatcher
from app.matching.outlier_filter import OutlierFilter
from app.matching.spatial_validator import SpatialCoverageValidator
from app.registration.subpixel import SubPixelRefiner
from app.registration.warper import ImageWarper, ndarray_to_base64_png
from app.registration.metrics import RegistrationMetricsCalculator
from app.models.schemas import MatchResponse, TiePoint, Point2D, RegistrationMetrics, BenchmarkRow

class LunarCorrespondencePipeline:
    def __init__(self):
        self.prebuilt_datasets = get_prebuilt_lunar_datasets()

    def get_available_datasets(self) -> Dict[str, Any]:
        return self.prebuilt_datasets

    def run_correspondence(
        self, 
        dataset_id: str = "dataset_scale_ohrc_tmc2", 
        method: str = "HYBRID_PHASE_CONGRUENCY",
        ransac_thresh: float = 3.0,
        enable_subpixel: bool = True,
        custom_img1: Optional[np.ndarray] = None,
        custom_img2: Optional[np.ndarray] = None
    ) -> MatchResponse:
        t0 = time.time()

        if custom_img1 is not None and custom_img2 is not None:
            img1 = custom_img1
            img2 = custom_img2
            dataset_meta = {
                "img1_res_m": 0.25,
                "img2_res_m": 0.25,
                "img1_source": "User Upload 1",
                "img2_source": "User Upload 2"
            }
        else:
            if dataset_id not in self.prebuilt_datasets:
                dataset_id = "dataset_scale_ohrc_tmc2"
            dataset_meta = self.prebuilt_datasets[dataset_id]
            img1 = dataset_meta["img1"]
            img2 = dataset_meta["img2"]

        # 1. Scale Ratio Check
        scale_ratio = dataset_meta.get("img2_res_m", 1.0) / max(0.01, dataset_meta.get("img1_res_m", 1.0))
        
        # 2. Hybrid Feature Matching
        match_res = HybridFeatureMatcher.match_multi_modal_hybrid(
            img1, 
            img2, 
            method=method, 
            scale_ratio=scale_ratio
        )
        pts1 = match_res["pts1"]
        pts2 = match_res["pts2"]
        pc1 = match_res["pc1"]
        pc2 = match_res["pc2"]

        # 3. Geometric RANSAC Outlier Filtering
        H, inliers_mask, inlier_ratio = OutlierFilter.estimate_homography_ransac(
            pts1, 
            pts2, 
            ransac_thresh=ransac_thresh
        )

        # 4. Spatial Coverage Validation
        inlier_pts1 = pts1[inliers_mask] if len(pts1) > 0 and len(inliers_mask) > 0 else np.array([])
        inlier_pts2 = pts2[inliers_mask] if len(pts2) > 0 and len(inliers_mask) > 0 else np.array([])
        
        spatial_data = SpatialCoverageValidator.calculate_spatial_distribution(
            pts=inlier_pts1,
            img_shape=img1.shape,
            grid_rows=4,
            grid_cols=4
        )

        # 5. Real Sub-Pixel Refinement
        subpixel_data = {
            "status": "Planned / Disabled",
            "enabled": False,
            "initial_rmse_pixels": 0.0,
            "refined_rmse_pixels": 0.0,
            "improvement_delta_pct": 0.0
        }

        if enable_subpixel and len(inlier_pts1) >= 4 and H is not None:
            subpixel_data = SubPixelRefiner.evaluate_subpixel_refinement(
                img1=img1,
                img2=img2,
                inlier_pts1=inlier_pts1,
                inlier_pts2=inlier_pts2,
                H_initial=H
            )
            # Use refined homography if available and within error tolerance
            if (subpixel_data.get("H_refined") is not None and 
                subpixel_data.get("refined_rmse_pixels", 999.0) <= max(1.5, subpixel_data.get("initial_rmse_pixels", 999.0) * 1.15)):
                H = subpixel_data["H_refined"]

        # Fallback identity if no homography found
        has_valid_h = H is not None
        if H is None:
            H = np.eye(3, dtype=np.float32)
            inliers_mask = np.zeros(len(pts1), dtype=bool)

        # 6. Warp & Generate Composite Overlays
        warp_dict = ImageWarper.warp_and_blend(img1, img2, H)
        warped_img2 = warp_dict["warped"]
        diff_map = warp_dict["difference"]
        blended_overlay = warp_dict["overlay"]

        t1 = time.time()
        exec_ms = (t1 - t0) * 1000.0

        # 7. Compute Scientific Metrics with Honest Diagnostics
        metrics_dict = RegistrationMetricsCalculator.calculate_metrics(
            pts1=pts1,
            pts2=pts2,
            inliers_mask=inliers_mask,
            H=H if has_valid_h else None,
            img1=img1,
            warped_img2=warped_img2,
            spatial_data=spatial_data,
            subpixel_data=subpixel_data,
            pixel_res_meters=dataset_meta.get("img1_res_m", 0.25),
            execution_time_ms=exec_ms
        )

        # 8. Individual Point Diagnostics (Exact Error + Rejection Reason)
        individual_errors = RegistrationMetricsCalculator.calculate_individual_errors(
            pts1=pts1,
            pts2=pts2,
            inliers_mask=inliers_mask,
            H=H if has_valid_h else None,
            ransac_thresh=ransac_thresh
        )

        tie_points_list = []
        for i in range(len(pts1)):
            err_info = individual_errors[i] if i < len(individual_errors) else {}
            tie_points_list.append(
                TiePoint(
                    id=i + 1,
                    pt1=Point2D(x=float(pts1[i][0]), y=float(pts1[i][1])),
                    pt2=Point2D(x=float(pts2[i][0]), y=float(pts2[i][1])),
                    confidence=0.95 if inliers_mask[i] else 0.35,
                    is_inlier=bool(inliers_mask[i]),
                    reprojection_error=err_info.get("reprojection_error"),
                    rejection_reason=err_info.get("rejection_reason")
                )
            )

        return MatchResponse(
            dataset_id=dataset_id,
            method_used=method,
            tie_points=tie_points_list,
            metrics=RegistrationMetrics(**metrics_dict),
            homography_matrix=[[round(float(v), 5) for v in row] for row in H] if has_valid_h else None,
            transformation_model="Projective Homography" if has_valid_h else "Estimation Failed",
            transformation_note="Computed from verified inliers via RANSAC." if has_valid_h else "Homography could not be reliably estimated (<4 inliers).",
            img1_base64=ndarray_to_base64_png(img1),
            img2_base64=ndarray_to_base64_png(img2),
            warped_img2_base64=ndarray_to_base64_png(warped_img2),
            difference_map_base64=ndarray_to_base64_png(diff_map),
            blended_overlay_base64=ndarray_to_base64_png(blended_overlay),
            phase_map1_base64=ndarray_to_base64_png(pc1) if pc1 is not None else None,
            phase_map2_base64=ndarray_to_base64_png(pc2) if pc2 is not None else None
        )

    def run_benchmark_suite(self, dataset_id: str = "dataset_scale_ohrc_tmc2") -> List[BenchmarkRow]:
        """
        Executes implemented algorithms and honestly documents planned models.
        """
        rows = []
        
        # 1. Classical SIFT (Executed)
        res_sift = self.run_correspondence(dataset_id=dataset_id, method="CLASSICAL_SIFT")
        m_sift = res_sift.metrics
        rows.append(
            BenchmarkRow(
                algorithm="Classical SIFT (Baseline)",
                category="Gradient Intensity",
                status="IMPLEMENTED",
                candidate_matches=m_sift.total_matches,
                inliers=m_sift.inlier_count,
                inlier_ratio=m_sift.inlier_ratio,
                rmse_pixels=m_sift.rmse_pixels if m_sift.inlier_count >= 4 else None,
                spatial_coverage_pct=m_sift.spatial_coverage_pct,
                runtime_ms=m_sift.execution_time_ms,
                notes="Standard OpenCV SIFT on raw intensity; breaks down under 180° illumination flips."
            )
        )

        # 2. LunaAlign Hybrid (Phase Congruency + RANSAC) (Executed)
        res_hybrid = self.run_correspondence(dataset_id=dataset_id, method="HYBRID_PHASE_CONGRUENCY")
        m_hybrid = res_hybrid.metrics
        rows.append(
            BenchmarkRow(
                algorithm="LunaAlign Hybrid (Phase Congruency + RANSAC)",
                category="Frequency Energy & Topography",
                status="IMPLEMENTED",
                candidate_matches=m_hybrid.total_matches,
                inliers=m_hybrid.inlier_count,
                inlier_ratio=m_hybrid.inlier_ratio,
                rmse_pixels=m_hybrid.rmse_pixels,
                spatial_coverage_pct=m_hybrid.spatial_coverage_pct,
                runtime_ms=m_hybrid.execution_time_ms,
                notes="Illumination-invariant log-Gabor energy maps + crater geometry; maintains inliers across shadow flips."
            )
        )

        # 3. RIFT (Radiation-variation Insensitive Feature Transform)
        rows.append(
            BenchmarkRow(
                algorithm="RIFT (Radiation Insensitive Feature Transform)",
                category="Multi-Modal / Spectral",
                status="PLANNED / EXPERIMENTAL",
                candidate_matches=0,
                inliers=0,
                inlier_ratio=0.0,
                rmse_pixels=None,
                spatial_coverage_pct=None,
                runtime_ms=0.0,
                notes="Planned multi-modal algorithm for optical vs SAR/IIRS matching. Not evaluated on this build."
            )
        )

        # 4. LoFTR (Local Feature TRansformer)
        rows.append(
            BenchmarkRow(
                algorithm="LoFTR (Deep Detector-Free Transformer)",
                category="Deep Learning",
                status="PLANNED / EXPERIMENTAL",
                candidate_matches=0,
                inliers=0,
                inlier_ratio=0.0,
                rmse_pixels=None,
                spatial_coverage_pct=None,
                runtime_ms=0.0,
                notes="Transformer self-attention cross-matcher; requires GPU PyTorch planetary pre-trained checkpoint."
            )
        )

        return rows

pipeline = LunarCorrespondencePipeline()
