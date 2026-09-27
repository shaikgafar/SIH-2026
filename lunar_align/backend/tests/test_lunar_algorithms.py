import pytest
import numpy as np
import cv2

from app.core.synthetic_lunar import generate_lunar_dem, render_lunar_hillshade, get_prebuilt_lunar_datasets
from app.preprocessing.phase_congruency import compute_phase_congruency_fast
from app.matching.crater_detector import CraterDetector
from app.matching.feature_matcher import HybridFeatureMatcher
from app.matching.outlier_filter import OutlierFilter
from app.core.pipeline import pipeline

def test_dem_and_photometric_rendering():
    dem = generate_lunar_dem(size=128, seed=42)
    assert dem.shape == (128, 128)
    assert dem.max() > dem.min()

    img = render_lunar_hillshade(dem, sun_azimuth_deg=45.0, sun_elevation_deg=30.0)
    assert img.shape == (128, 128)
    assert img.dtype == np.uint8
    assert np.mean(img) > 10

def test_phase_congruency_illumination_invariance():
    dem = generate_lunar_dem(size=128, seed=99)
    # Morning sun (east illumination) vs Afternoon sun (west illumination)
    img_morning = render_lunar_hillshade(dem, sun_azimuth_deg=45.0, sun_elevation_deg=25.0)
    img_afternoon = render_lunar_hillshade(dem, sun_azimuth_deg=225.0, sun_elevation_deg=25.0)

    pc_m = compute_phase_congruency_fast(img_morning, n_scales=2, n_orientations=3)
    pc_a = compute_phase_congruency_fast(img_afternoon, n_scales=2, n_orientations=3)

    assert pc_m.shape == (128, 128)
    assert pc_a.shape == (128, 128)
    # Both phase congruency maps should capture edges rather than homogeneous shadow blocks
    assert np.std(pc_m) > 8.0
    assert np.std(pc_a) > 8.0

def test_crater_rim_detection():
    dem = generate_lunar_dem(size=256, seed=10)
    img = render_lunar_hillshade(dem, sun_azimuth_deg=90.0, sun_elevation_deg=35.0)
    
    craters = CraterDetector.detect_crater_rims(img, min_radius=6, max_radius=120)
    assert len(craters) >= 1
    # Check that detected craters have valid centers and radii
    for c in craters:
        assert 0 <= c["center"][0] <= 256
        assert 0 <= c["center"][1] <= 256
        assert c["radius"] > 5.0

def test_ransac_homography_estimation():
    # Synthetic ground truth affine/homography transform
    pts1 = np.float32([[20, 20], [180, 25], [190, 180], [30, 195], [100, 100], [70, 140]])
    H_true = np.array([
        [1.05, -0.02, 12.0],
        [0.02,  1.03, -8.0],
        [0.0,   0.0,   1.0]
    ], dtype=np.float32)

    pts1_homo = np.hstack([pts1, np.ones((len(pts1), 1))])
    pts2 = (H_true @ pts1_homo.T).T[:, :2]

    # Add 1 outlier
    pts2_with_outlier = np.vstack([pts2, [500, 500]])
    pts1_with_outlier = np.vstack([pts1, [50, 50]])

    H_est, mask, inlier_ratio = OutlierFilter.estimate_homography_ransac(
        pts1_with_outlier, pts2_with_outlier, ransac_thresh=3.0
    )

    assert H_est is not None
    assert inlier_ratio >= 0.80 # 6 out of 7 points are inliers
    assert mask[-1] == False # Outlier is successfully rejected!

def test_end_to_end_pipeline_scale_invariance():
    res = pipeline.run_correspondence(
        dataset_id="dataset_scale_ohrc_tmc2",
        method="HYBRID_PHASE_CONGRUENCY",
        ransac_thresh=4.0
    )

    assert res.metrics.inlier_count > 0
    assert len(res.tie_points) > 0
    assert res.homography_matrix is not None
    assert len(res.warped_img2_base64) > 100
    assert len(res.difference_map_base64) > 100

def test_end_to_end_pipeline_sun_angle_invariance():
    res = pipeline.run_correspondence(
        dataset_id="dataset_sun_angle_crater",
        method="HYBRID_PHASE_CONGRUENCY",
        ransac_thresh=4.0
    )

    assert res.metrics.inlier_count > 0
    assert res.metrics.rmse_pixels < 3.5
