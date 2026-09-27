from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any

class Point2D(BaseModel):
    x: float
    y: float

class TiePoint(BaseModel):
    id: int
    pt1: Point2D # Coordinates in Image 1
    pt2: Point2D # Coordinates in Image 2
    confidence: float
    is_inlier: bool = True
    reprojection_error: Optional[float] = None
    rejection_reason: Optional[str] = None

class RegistrationMetrics(BaseModel):
    # Geometric Reprojection Metrics
    rmse_pixels: float
    estimated_ground_error_meters: Optional[float] = None
    ground_truth_note: str = "Independent ground truth: unavailable"
    
    # Inlier Quality
    inlier_count: int
    total_matches: int
    inlier_ratio: float
    
    # Spatial Distribution
    spatial_coverage_pct: float = 0.0
    spatial_warning: Optional[str] = None
    
    # Registration Confidence Score
    confidence_level: str = "LOW" # HIGH, MEDIUM, LOW, FAILED
    confidence_reason: str = ""
    
    # Sub-Pixel Refinement
    subpixel_status: str = "Planned"
    initial_rmse_pixels: float = 0.0
    refined_rmse_pixels: float = 0.0
    subpixel_delta_pct: float = 0.0
    
    # Spectral and Correlation Metrics
    nmi_score: float # Normalized Mutual Information
    ssim_score: float # Structural Similarity
    scale_ratio_estimated: float # Image-space transformation scale
    rotation_deg_estimated: float
    
    # Performance & System
    execution_time_ms: float
    hardware_info: str = "Platform CPU"

class MatchRequest(BaseModel):
    dataset_id: Optional[str] = "dataset_scale_ohrc_tmc2"
    method: Optional[str] = "HYBRID_PHASE_CONGRUENCY"
    ransac_thresh: Optional[float] = 3.0
    enable_subpixel: Optional[bool] = True

class MatchResponse(BaseModel):
    dataset_id: str
    method_used: str
    tie_points: List[TiePoint]
    metrics: RegistrationMetrics
    homography_matrix: Optional[List[List[float]]] = None
    transformation_model: str = "Projective Homography"
    transformation_note: str = "Computed from verified correspondences via RANSAC."
    img1_base64: str
    img2_base64: str
    warped_img2_base64: str
    difference_map_base64: str
    blended_overlay_base64: str
    phase_map1_base64: Optional[str] = None
    phase_map2_base64: Optional[str] = None

class LunarDatasetInfo(BaseModel):
    id: str
    title: str
    description: str
    category: str # PRIMARY_CHANDRAYAAN vs REFERENCE_VALIDATION
    challenge_type: str # SCALE_INVARIANCE, SUN_ANGLE_INVARIANCE, CROSS_MISSION
    img1_source: str
    img2_source: str
    img1_res_m: float
    img2_res_m: float
    sun_azimuth_1: float
    sun_azimuth_2: float
    sun_elevation_1: float
    sun_elevation_2: float
    lunar_target: str
    provenance_source: str
    product_id_1: Optional[str] = None
    product_id_2: Optional[str] = None
    archive_url_1: Optional[str] = None
    archive_url_2: Optional[str] = None
    download_url_2: Optional[str] = None
    acquisition_date_1: Optional[str] = None
    acquisition_date_2: Optional[str] = None
    processing_status: str = "Pre-calibrated benchmark"

class BenchmarkRow(BaseModel):
    algorithm: str
    category: str
    status: str # IMPLEMENTED vs PLANNED
    candidate_matches: int
    inliers: int
    inlier_ratio: float
    rmse_pixels: Optional[float] = None
    spatial_coverage_pct: Optional[float] = None
    runtime_ms: float
    notes: str
