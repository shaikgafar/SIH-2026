# LunaAlign (SIH26166) — Planetary Lunar Image Correspondence Engine

**Automated Multi-Modal, Scale-Invariant, and Illumination-Robust Image Registration for ISRO Chandrayaan-2 Datasets.**

---

## 🌕 Overview

LunaAlign is a specialized computer vision and image registration engine designed to solve the primary challenges of planetary optical imaging:
1. **Multi-Sensor Domain Gaps:** Aligning high-resolution Chandrayaan-2 OHRC (0.25m/px) with medium-resolution TMC-2 (5.0m/px) or NASA LRO NAC (0.5m/px).
2. **Extreme Illumination & Sun-Angle Variation:** Handling inverted crater shadows and photometric changes across orbits (up to 180° solar azimuth shifts).
3. **Sub-Pixel Precision:** Achieving reprojection accuracy $< 1.0\text{ px}$ with gradient-based corner refinement and robust RANSAC projective homography.

---

## 🔬 Scientific Pipeline

```
[1. Input Rasters] ──> [2. Phase Congruency] ──> [3. Feature Extraction] ──> [4. RANSAC Homography] ──> [5. Sub-Pixel Alignment]
```

- **Phase Congruency (Log-Gabor Filter Banks):** Extracts illumination-invariant frequency domain features where Fourier components align in phase, making feature detection robust to shadow flips and severe contrast differences.
- **Topographic & Crater Geometry:** Validates keypoint distributions using a 4×4 spatial quadrant check to eliminate localized clustering.
- **RANSAC Inlier Verification:** Filters out false correspondence matches and computes a projective 3×3 homography matrix ($H$).
- **Sub-Pixel Refinement (`cv2.cornerSubPix`):** Optimizes tie-points to sub-pixel coordinates.

---

## 🚀 Quick Start Guide

### 1. Launch LunaAlign Backend (Port 8001)
Double-click `run_lunar_backend.bat` or run:
```powershell
cd lunar_align\backend
.\venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```
API Documentation (Swagger UI) is available at: `http://localhost:8001/docs`

### 2. Launch Frontend Dashboard (Port 5173)
Double-click `run_frontend.bat` or run:
```powershell
cd frontend
npm run dev
```
Open your browser at: `http://localhost:5173`

---

## 📊 Pre-Loaded Datasets

1. **Scale Invariance:** Chandrayaan-2 OHRC (0.25m) vs TMC-2 (5.0m) — 20x resolution gap.
2. **Sun-Angle Invariance:** Morning Sun (40°) vs Afternoon Sun (220°) — 180° solar flip.
3. **Cross-Mission Validation:** Chandrayaan-2 OHRC vs NASA LRO NAC.
4. **Custom Upload:** Upload custom planetary image pairs (PNG, JPG, TIFF) for on-the-fly registration.
