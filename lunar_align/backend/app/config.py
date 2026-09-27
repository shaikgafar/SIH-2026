import os
from pathlib import Path

class Settings:
    PROJECT_NAME: str = "SIH26166 - Multi-Modal Lunar Image Correspondence (ISRO Chandrayaan-2)"
    API_V1_STR: str = "/api"
    
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    CACHE_DIR: Path = BASE_DIR / "cache"

    # Default Algorithm Parameters
    DEFAULT_RANSAC_THRESH: float = 3.0
    DEFAULT_INLIER_RATIO_MIN: float = 0.35
    DEFAULT_MIN_MATCHES: int = 8
    
    # Scale Pyramid Levels
    MAX_PYRAMID_LEVELS: int = 4
    
    # Phase Congruency Settings (Kovesi algorithm parameters)
    PC_N_SCALES: int = 4
    PC_N_ORIENTATIONS: int = 6
    PC_MIN_WAVELENGTH: float = 3.0
    PC_MULT: float = 2.1
    PC_SIGMA_ON_F: float = 0.55

settings = Settings()
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.CACHE_DIR.mkdir(parents=True, exist_ok=True)
