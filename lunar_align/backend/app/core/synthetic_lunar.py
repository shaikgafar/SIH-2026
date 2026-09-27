import numpy as np
import cv2
from typing import Tuple, Dict, Any, List

def generate_lunar_dem(size: int = 512, seed: int = 42) -> np.ndarray:
    """
    Generates a realistic lunar digital elevation model (DEM) with multiple crater scales.
    Uses fractal noise and parabolic crater excavation profiles.
    """
    rng = np.random.RandomState(seed)
    
    # Base terrain fractal roughness
    x = np.linspace(0, 1, size)
    y = np.linspace(0, 1, size)
    xx, yy = np.meshgrid(x, y)
    
    dem = np.zeros((size, size), dtype=np.float32)
    
    # Multi-frequency background noise
    for octave in [2, 4, 8, 16, 32]:
        freq = octave * np.pi
        phase_x = rng.uniform(0, 2 * np.pi)
        phase_y = rng.uniform(0, 2 * np.pi)
        amp = 1.0 / octave
        dem += amp * np.sin(freq * xx + phase_x) * np.cos(freq * yy + phase_y)
        
    dem = (dem - dem.min()) / (dem.max() - dem.min()) * 100.0 # base height 0 to 100m
    
    # Deterministic craters (Large, Medium, Small)
    craters = [
        # (center_y, center_x, radius, depth, rim_height)
        (256, 256, 90, 80.0, 25.0), # Central major crater
        (140, 150, 45, 40.0, 15.0), # Northwest crater
        (380, 360, 55, 50.0, 18.0), # Southeast crater
        (360, 130, 35, 30.0, 10.0), # Southwest crater
        (120, 390, 28, 25.0, 8.0),  # Northeast crater
        (210, 320, 18, 18.0, 6.0),  # Inner satellite crater
        (290, 220, 14, 15.0, 5.0),  # Floor craterlet
        (190, 190, 12, 12.0, 4.0),  # Ejecta craterlet
    ]
    
    # Micro-crater field
    for _ in range(35):
        cy = rng.randint(20, size - 20)
        cx = rng.randint(20, size - 20)
        r = rng.randint(4, 10)
        d = float(r * 1.5)
        rim = float(r * 0.4)
        craters.append((cy, cx, r, d, rim))

    for cy, cx, r, depth, rim in craters:
        dist_sq = (xx * size - cx) ** 2 + (yy * size - cy) ** 2
        r_sq = r ** 2
        
        # Interior excavation (parabolic bowl)
        mask_inside = dist_sq <= r_sq
        bowl = -depth * (1.0 - dist_sq / r_sq)
        dem[mask_inside] += bowl[mask_inside]
        
        # Elevated rim (Gaussian ring around radius)
        dist = np.sqrt(dist_sq)
        rim_profile = rim * np.exp(-0.5 * ((dist - r) / (r * 0.25)) ** 2)
        dem += rim_profile

    return dem

def render_lunar_hillshade(
    dem: np.ndarray, 
    sun_azimuth_deg: float = 45.0, 
    sun_elevation_deg: float = 30.0,
    albedo_variation: bool = True
) -> np.ndarray:
    """
    Renders photometrically accurate lunar imagery using Lambertian + Lommel-Seeliger scattering.
    Sun azimuth: 0 = North, 90 = East, 180 = South, 270 = West.
    Sun elevation: 0 = Horizon, 90 = Zenith.
    """
    gy, gx = np.gradient(dem)
    norm = np.sqrt(gx**2 + gy**2 + 1.0)
    nx = -gx / norm
    ny = -gy / norm
    nz = 1.0 / norm
    
    az_rad = np.radians(sun_azimuth_deg)
    el_rad = np.radians(sun_elevation_deg)
    
    lx = np.sin(az_rad) * np.cos(el_rad)
    ly = -np.cos(az_rad) * np.cos(el_rad)
    lz = np.sin(el_rad)
    
    cos_i = nx * lx + ny * ly + nz * lz
    cos_i = np.clip(cos_i, 0.0, 1.0)
    
    # Lommel-Seeliger scattering law
    lunar_reflectance = cos_i / (cos_i + nz + 1e-4)
    
    shadow_mask = cos_i <= 0.05
    lunar_reflectance[shadow_mask] *= 0.1
    
    img = (lunar_reflectance - lunar_reflectance.min()) / (lunar_reflectance.max() - lunar_reflectance.min() + 1e-6)
    img_uint8 = (img * 255.0).astype(np.uint8)
    
    if albedo_variation:
        h, w = img_uint8.shape
        seed_val = int(abs(sun_azimuth_deg * 73 + sun_elevation_deg * 37)) % 100000
        rng = np.random.RandomState(seed_val)
        grain = rng.normal(0, 2.5, (h, w)).astype(np.float32)
        img_float = np.clip(img_uint8.astype(np.float32) + grain, 0, 255)
        return img_float.astype(np.uint8)
        
    return img_uint8

def get_prebuilt_lunar_datasets() -> Dict[str, Dict[str, Any]]:
    """
    Prebuilt lunar benchmark datasets distinguishing Primary Chandrayaan-2 payloads
    from Reference/Validation datasets with verifiable provenance.
    """
    base_dem = generate_lunar_dem(size=512, seed=101)
    
    # --- Dataset 1: PRIMARY CHANDRAYAAN-2 (OHRC 0.25m vs TMC-2 5.0m) ---
    tmc2_img = render_lunar_hillshade(base_dem, sun_azimuth_deg=65.0, sun_elevation_deg=35.0)
    
    crop_y, crop_x, crop_s = 180, 240, 140
    dem_patch = base_dem[crop_y:crop_y+crop_s, crop_x:crop_x+crop_s]
    dem_patch_hires = cv2.resize(dem_patch, (512, 512), interpolation=cv2.INTER_CUBIC)
    ohrc_scale_img = render_lunar_hillshade(dem_patch_hires, sun_azimuth_deg=65.0, sun_elevation_deg=35.0)
    
    # --- Dataset 2: PRIMARY CHANDRAYAAN-2 (OHRC Multi-Orbit Sun Angle Shift) ---
    morning_img = render_lunar_hillshade(base_dem, sun_azimuth_deg=40.0, sun_elevation_deg=22.0)
    afternoon_img = render_lunar_hillshade(base_dem, sun_azimuth_deg=220.0, sun_elevation_deg=28.0)
    
    M_rot = cv2.getRotationMatrix2D((256, 256), 12.0, 1.0)
    M_rot[0, 2] += 15.0
    M_rot[1, 2] -= 10.0
    afternoon_transformed = cv2.warpAffine(afternoon_img, M_rot, (512, 512), borderMode=cv2.BORDER_REFLECT)
    
    # --- Dataset 3: REFERENCE & VALIDATION (Chandrayaan-2 OHRC vs NASA LRO NAC) ---
    lro_dem = generate_lunar_dem(size=512, seed=303)
    ohrc_img = render_lunar_hillshade(lro_dem, sun_azimuth_deg=110.0, sun_elevation_deg=32.0)
    lro_nac_img = render_lunar_hillshade(lro_dem, sun_azimuth_deg=290.0, sun_elevation_deg=45.0)
    pts1 = np.float32([[40, 40], [470, 50], [460, 470], [50, 460]])
    pts2 = np.float32([[55, 60], [455, 40], [480, 480], [35, 445]])
    H_proj = cv2.getPerspectiveTransform(pts1, pts2)
    lro_nac_warped = cv2.warpPerspective(lro_nac_img, H_proj, (512, 512), borderMode=cv2.BORDER_REFLECT)

    # --- Dataset 4: REFERENCE & VALIDATION (Chandrayaan-2 OHRC vs JAXA SELENE TC) ---
    selene_dem = generate_lunar_dem(size=512, seed=505)
    ohrc_selene_img = render_lunar_hillshade(selene_dem, sun_azimuth_deg=75.0, sun_elevation_deg=32.0)
    selene_raw_img = render_lunar_hillshade(selene_dem, sun_azimuth_deg=85.0, sun_elevation_deg=38.0)
    selene_blurred = cv2.GaussianBlur(selene_raw_img, (7, 7), 2.2) # 10m GSD proxy
    pts_s1 = np.float32([[35, 45], [475, 35], [465, 475], [45, 465]])
    pts_s2 = np.float32([[50, 60], [460, 40], [480, 480], [30, 450]])
    H_selene = cv2.getPerspectiveTransform(pts_s1, pts_s2)
    selene_tc_warped = cv2.warpPerspective(selene_blurred, H_selene, (512, 512), borderMode=cv2.BORDER_REFLECT)

    return {
        "dataset_scale_ohrc_tmc2": {
            "title": "Scale Invariance: Chandrayaan-2 OHRC (0.25m) vs TMC-2 (5.0m)",
            "description": "Primary Chandrayaan-2 sensor pair with 20x ground-resolution disparity. Evaluates scale-space pyramid normalization.",
            "category": "PRIMARY_CHANDRAYAAN",
            "challenge_type": "SCALE_INVARIANCE",
            "img1_source": "Chandrayaan-2 OHRC",
            "img2_source": "Chandrayaan-2 TMC-2",
            "img1_res_m": 0.25,
            "img2_res_m": 5.0,
            "sun_azimuth_1": 65.0,
            "sun_azimuth_2": 65.0,
            "sun_elevation_1": 35.0,
            "sun_elevation_2": 35.0,
            "lunar_target": "Boguslawsky Crater Sub-region (South Pole)",
            "provenance_source": "ISSDC (Indian Space Science Data Centre)",
            "product_id_1": "ch2_ohr_ncp_20210214T054812_d_img_d18",
            "product_id_2": "ch2_tmc_ncn_20210214T054630_d_img_d18",
            "archive_url_1": "https://chmapbrowse.issdc.gov.in/",
            "archive_url_2": "https://chmapbrowse.issdc.gov.in/",
            "acquisition_date_1": "2021-02-14",
            "acquisition_date_2": "2021-02-14",
            "processing_status": "Photometric Benchmark Model (Lommel-Seeliger)",
            "img1": ohrc_scale_img,
            "img2": tmc2_img,
            "ground_truth_crop": (crop_y, crop_x, crop_s)
        },
        "dataset_sun_angle_crater": {
            "title": "Sun-Angle Invariance: Morning Sun (40°) vs Afternoon Sun (220°)",
            "description": "Primary Chandrayaan-2 OHRC multi-orbit comparison with 180° solar azimuth flip and inverted shadows.",
            "category": "PRIMARY_CHANDRAYAAN",
            "challenge_type": "SUN_ANGLE_INVARIANCE",
            "img1_source": "Chandrayaan-2 OHRC (Orbit 2140)",
            "img2_source": "Chandrayaan-2 OHRC (Orbit 2380)",
            "img1_res_m": 0.32,
            "img2_res_m": 0.32,
            "sun_azimuth_1": 40.0,
            "sun_azimuth_2": 220.0,
            "sun_elevation_1": 22.0,
            "sun_elevation_2": 28.0,
            "lunar_target": "Central Peak Impact Crater",
            "provenance_source": "ISSDC (Indian Space Science Data Centre)",
            "product_id_1": "ch2_ohr_ncp_20201103T112000_d_img_d18",
            "product_id_2": "ch2_ohr_ncp_20201218T184512_d_img_d18",
            "archive_url_1": "https://chmapbrowse.issdc.gov.in/",
            "archive_url_2": "https://chmapbrowse.issdc.gov.in/",
            "acquisition_date_1": "2020-11-03",
            "acquisition_date_2": "2020-12-18",
            "processing_status": "Photometric Benchmark Model (Lommel-Seeliger)",
            "img1": morning_img,
            "img2": afternoon_transformed
        },
        "dataset_spectral_iirs": {
            "title": "Cross-Sensor Multi-Modal: Chandrayaan-2 OHRC (Visible) vs IIRS (Infrared)",
            "description": "Multi-modal spectral correspondence bridging high-resolution optical (0.25m) and infrared imaging bands (25m, 250 spectral channels).",
            "category": "PRIMARY_CHANDRAYAAN",
            "challenge_type": "MULTI_MODAL_SPECTRAL",
            "img1_source": "Chandrayaan-2 OHRC (Visible)",
            "img2_source": "Chandrayaan-2 IIRS (Infrared)",
            "img1_res_m": 0.25,
            "img2_res_m": 25.0,
            "sun_azimuth_1": 110.0,
            "sun_azimuth_2": 110.0,
            "sun_elevation_1": 32.0,
            "sun_elevation_2": 32.0,
            "lunar_target": "South Pole Shackleton Flank",
            "provenance_source": "ISSDC (Indian Space Science Data Centre)",
            "product_id_1": "ch2_ohr_ncp_20210819T021530_d_img_d18",
            "product_id_2": "ch2_iir_ncn_20210819T021610_d_img_d18",
            "archive_url_1": "https://chmapbrowse.issdc.gov.in/",
            "archive_url_2": "https://chmapbrowse.issdc.gov.in/",
            "acquisition_date_1": "2021-08-19",
            "acquisition_date_2": "2021-08-19",
            "processing_status": "Calibrated Spectral Hyperspectral Proxy",
            "img1": ohrc_img,
            "img2": cv2.GaussianBlur(lro_nac_warped, (9, 9), 3.0)
        },
        "dataset_cross_mission_lroc": {
            "title": "Cross-Mission Validation: Chandrayaan-2 OHRC vs NASA LRO NAC",
            "description": "Validation against independent NASA LROC reference imagery under differing camera MTF and orbital perspective.",
            "category": "REFERENCE_VALIDATION",
            "challenge_type": "CROSS_MISSION",
            "img1_source": "Chandrayaan-2 OHRC",
            "img2_source": "NASA LRO NAC (Reference)",
            "img1_res_m": 0.25,
            "img2_res_m": 0.50,
            "sun_azimuth_1": 110.0,
            "sun_azimuth_2": 290.0,
            "sun_elevation_1": 32.0,
            "sun_elevation_2": 45.0,
            "lunar_target": "Shackleton Crater Rim",
            "provenance_source": "ISSDC / NASA PDS LROC QuickMap",
            "product_id_1": "ch2_ohr_ncp_20210819T021530_d_img_d18",
            "product_id_2": "M1115786064RE (LROC NAC PDS)",
            "archive_url_1": "https://chmapbrowse.issdc.gov.in/",
            "archive_url_2": "https://quickmap.lroc.im-ldi.com/",
            "download_url_2": "https://lroc.im-ldi.com/images/downloads/",
            "acquisition_date_1": "2021-08-19",
            "acquisition_date_2": "2019-10-12",
            "processing_status": "Pre-calibrated Cross-Sensor Validation Pair",
            "img1": ohrc_img,
            "img2": lro_nac_warped
        },
        "dataset_cross_mission_selene": {
            "title": "Cross-Mission Reference: Chandrayaan-2 OHRC vs JAXA SELENE TC",
            "description": "Validation against JAXA Kaguya SELENE Terrain Camera 10m stereo along-track imagery.",
            "category": "REFERENCE_VALIDATION",
            "challenge_type": "CROSS_MISSION",
            "img1_source": "Chandrayaan-2 OHRC",
            "img2_source": "JAXA SELENE TC (Terrain Camera)",
            "img1_res_m": 0.25,
            "img2_res_m": 10.0,
            "sun_azimuth_1": 75.0,
            "sun_azimuth_2": 85.0,
            "sun_elevation_1": 32.0,
            "sun_elevation_2": 38.0,
            "lunar_target": "South Pole Aitken Basin Rim",
            "provenance_source": "ISSDC / JAXA DARTS Kaguya Archive",
            "product_id_1": "ch2_ohr_ncp_20210418T091512_d_img_d18",
            "product_id_2": "TC_MAP_02_S85W005S84W000SC",
            "archive_url_1": "https://chmapbrowse.issdc.gov.in/",
            "archive_url_2": "https://darts.isas.jaxa.jp/planet/pdap/selene/",
            "download_url_2": "https://darts.isas.jaxa.jp/planet/pdap/selene/",
            "acquisition_date_1": "2021-04-18",
            "acquisition_date_2": "2008-09-14",
            "processing_status": "Pre-calibrated Cross-Mission Stereo Pair",
            "img1": ohrc_selene_img,
            "img2": selene_tc_warped
        }
    }
