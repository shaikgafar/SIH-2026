import cv2
import numpy as np
from typing import Tuple, Dict, Any, List

class SpatialCoverageValidator:
    """
    Validates that verified tie-point inliers are well-distributed across the lunar image
    rather than clustered in a single crater or edge artifact.
    """
    @staticmethod
    def calculate_spatial_distribution(
        pts: np.ndarray, 
        img_shape: Tuple[int, int], 
        grid_rows: int = 4, 
        grid_cols: int = 4
    ) -> Dict[str, Any]:
        h, w = img_shape[:2]
        total_cells = grid_rows * grid_cols
        
        if len(pts) == 0:
            return {
                "coverage_pct": 0.0,
                "occupied_cells": 0,
                "total_cells": total_cells,
                "cell_counts": [[0 for _ in range(grid_cols)] for _ in range(grid_rows)],
                "is_clustered": True,
                "warning_message": "No correspondences available to assess spatial coverage."
            }

        cell_h = h / grid_rows
        cell_w = w / grid_cols
        
        grid = np.zeros((grid_rows, grid_cols), dtype=int)
        
        for pt in pts:
            x, y = pt[0], pt[1]
            c = int(np.clip(x // cell_w, 0, grid_cols - 1))
            r = int(np.clip(y // cell_h, 0, grid_rows - 1))
            grid[r, c] += 1
            
        occupied = int(np.count_nonzero(grid))
        coverage_pct = round((occupied / total_cells) * 100.0, 1)
        
        # Clustering detection: if coverage is < 25% or all points are in <= 2 cells
        is_clustered = False
        warning = None
        if len(pts) >= 4 and coverage_pct < 25.0:
            is_clustered = True
            warning = f"Spatial clustering warning: Correspondences cover only {coverage_pct}% of the image area."
        elif occupied <= 2 and len(pts) >= 6:
            is_clustered = True
            warning = f"Spatial clustering warning: {len(pts)} matches are concentrated in only {occupied} local grid cells."

        return {
            "coverage_pct": coverage_pct,
            "occupied_cells": occupied,
            "total_cells": total_cells,
            "cell_counts": grid.tolist(),
            "is_clustered": is_clustered,
            "warning_message": warning
        }
