import cv2
import numpy as np
from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import PlainTextResponse

from app.models.schemas import MatchRequest, MatchResponse, LunarDatasetInfo, BenchmarkRow
from app.core.pipeline import pipeline

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "status": "ok", 
        "mission": "Chandrayaan-2", 
        "service": "SIH26166 Multi-Modal Lunar Image Correspondence Engine",
        "supported_payloads": ["OHRC", "TMC-2", "IIRS", "LRO NAC", "SELENE"]
    }

@router.get("/datasets", response_model=List[LunarDatasetInfo])
def list_datasets():
    datasets = pipeline.get_available_datasets()
    results = []
    for d_id, data in datasets.items():
        results.append(
            LunarDatasetInfo(
                id=d_id,
                title=data["title"],
                description=data["description"],
                category=data.get("category", "PRIMARY_CHANDRAYAAN"),
                challenge_type=data["challenge_type"],
                img1_source=data["img1_source"],
                img2_source=data["img2_source"],
                img1_res_m=data["img1_res_m"],
                img2_res_m=data["img2_res_m"],
                sun_azimuth_1=data["sun_azimuth_1"],
                sun_azimuth_2=data["sun_azimuth_2"],
                sun_elevation_1=data["sun_elevation_1"],
                sun_elevation_2=data["sun_elevation_2"],
                lunar_target=data["lunar_target"],
                provenance_source=data.get("provenance_source", "ISSDC"),
                product_id_1=data.get("product_id_1"),
                product_id_2=data.get("product_id_2"),
                archive_url_1=data.get("archive_url_1", "https://chmapbrowse.issdc.gov.in/"),
                archive_url_2=data.get("archive_url_2"),
                download_url_2=data.get("download_url_2"),
                acquisition_date_1=data.get("acquisition_date_1"),
                acquisition_date_2=data.get("acquisition_date_2"),
                processing_status=data.get("processing_status", "Calibrated benchmark")
            )
        )
    return results

@router.post("/match", response_model=MatchResponse)
def match_images(req: MatchRequest):
    try:
        res = pipeline.run_correspondence(
            dataset_id=req.dataset_id or "dataset_scale_ohrc_tmc2",
            method=req.method or "HYBRID_PHASE_CONGRUENCY",
            ransac_thresh=req.ransac_thresh or 3.0,
            enable_subpixel=req.enable_subpixel if req.enable_subpixel is not None else True
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Matching pipeline failed: {str(e)}")

@router.get("/benchmark", response_model=List[BenchmarkRow])
def get_benchmark_comparison(dataset_id: str = "dataset_scale_ohrc_tmc2"):
    try:
        return pipeline.run_benchmark_suite(dataset_id=dataset_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload", response_model=MatchResponse)
async def upload_and_match(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
    method: str = Form("HYBRID_PHASE_CONGRUENCY"),
    ransac_thresh: float = Form(3.0),
    enable_subpixel: bool = Form(True)
):
    try:
        bytes1 = await file1.read()
        bytes2 = await file2.read()

        nparr1 = np.frombuffer(bytes1, np.uint8)
        nparr2 = np.frombuffer(bytes2, np.uint8)

        img1 = cv2.imdecode(nparr1, cv2.IMREAD_GRAYSCALE)
        img2 = cv2.imdecode(nparr2, cv2.IMREAD_GRAYSCALE)

        if img1 is None or img2 is None:
            raise HTTPException(
                status_code=400, 
                detail="Invalid image format. Supported formats: PNG, JPG, TIFF. (Scientific PDS/ISIS format support not enabled in this build)."
            )

        res = pipeline.run_correspondence(
            dataset_id="custom_upload",
            method=method,
            ransac_thresh=ransac_thresh,
            enable_subpixel=enable_subpixel,
            custom_img1=img1,
            custom_img2=img2
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/csv")
def export_tiepoints_csv(dataset_id: str = "dataset_scale_ohrc_tmc2"):
    res = pipeline.run_correspondence(dataset_id=dataset_id)
    lines = ["match_id,image_a_x,image_a_y,image_b_x,image_b_y,match_status,confidence,reprojection_error,rejection_reason"]
    for tp in res.tie_points:
        status_str = "INLIER" if tp.is_inlier else "OUTLIER"
        err_str = f"{tp.reprojection_error:.2f}" if tp.reprojection_error is not None else "N/A"
        reason_str = f'"{tp.rejection_reason}"' if tp.rejection_reason else "N/A"
        lines.append(
            f"{tp.id},{tp.pt1.x:.2f},{tp.pt1.y:.2f},{tp.pt2.x:.2f},{tp.pt2.y:.2f},{status_str},{tp.confidence:.2f},{err_str},{reason_str}"
        )
    return PlainTextResponse(content="\n".join(lines), media_type="text/csv")

@router.get("/export/report")
def export_registration_report(dataset_id: str = "dataset_scale_ohrc_tmc2"):
    res = pipeline.run_correspondence(dataset_id=dataset_id)
    m = res.metrics
    datasets = pipeline.get_available_datasets()
    data = datasets.get(dataset_id, {})

    h_str = "N/A (Estimation Failed)"
    if res.homography_matrix:
        h_str = "\n".join([f"  [ {', '.join([f'{v:10.5f}' for v in row])} ]" for row in res.homography_matrix])

    report = f"""# LunaAlign Scientific Registration Report (SIH26166)

**Mission / Domain:** ISRO Chandrayaan-2 Optical Payloads (Space Technology)
**Dataset ID:** {dataset_id}
**Primary Target:** {data.get('lunar_target', 'Lunar Surface')}
**Provenance Source:** {data.get('provenance_source', 'ISSDC')}
**Processing Status:** {data.get('processing_status', 'Evaluated')}

---

## 1. Sensor & Acquisition Metadata
- **Image A (Target):** {data.get('img1_source', 'N/A')}
  - Product ID: {data.get('product_id_1', 'Metadata unavailable')}
  - Ground Resolution: {data.get('img1_res_m', 'N/A')} m/pixel
  - Sun Azimuth / Elevation: {data.get('sun_azimuth_1', 'N/A')}° / {data.get('sun_elevation_1', 'N/A')}°
- **Image B (Reference):** {data.get('img2_source', 'N/A')}
  - Product ID: {data.get('product_id_2', 'Metadata unavailable')}
  - Ground Resolution: {data.get('img2_res_m', 'N/A')} m/pixel
  - Sun Azimuth / Elevation: {data.get('sun_azimuth_2', 'N/A')}° / {data.get('sun_elevation_2', 'N/A')}°

---

## 2. Geometric Verification & Transformation
- **Transformation Model:** {res.transformation_model}
- **Method Executed:** {res.method_used}
- **Homography Matrix (H):**
{h_str}

---

## 3. Quantitative Validation Metrics
- **Candidate Matches:** {m.total_matches}
- **Verified Inliers:** {m.inlier_count}
- **Inlier Ratio:** {m.inlier_ratio * 100:.1f}%
- **Reprojection RMSE:** {m.rmse_pixels} pixels
- **Estimated Ground Error:** {m.estimated_ground_error_meters} meters ({m.ground_truth_note})
- **Spatial Coverage:** {m.spatial_coverage_pct}%
- **Spatial Clustering Warning:** {m.spatial_warning or 'None (Well distributed)'}
- **Sub-Pixel Refinement:** {m.subpixel_status} (Δ = {m.subpixel_delta_pct}%)
  - Initial RMSE: {m.initial_rmse_pixels} px
  - Refined RMSE: {m.refined_rmse_pixels} px
- **Normalized Mutual Information (NMI):** {m.nmi_score}
- **Structural Similarity (SSIM):** {m.ssim_score}
- **Image-Space Transformation Scale:** {m.scale_ratio_estimated}x
- **Estimated Rotation:** {m.rotation_deg_estimated}°
- **Execution Processing Time:** {m.execution_time_ms} ms
- **Hardware Platform:** {m.hardware_info}

---

## 4. Scientific Registration Quality Verdict
- **Confidence Level:** {m.confidence_level}
- **Reason:** {m.confidence_reason}

*Report generated by LunaAlign Studio — SIH26166 Prototype.*
"""
    return PlainTextResponse(content=report, media_type="text/markdown")
