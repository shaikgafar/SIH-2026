import cv2
import numpy as np
from typing import List, Tuple

class ScalePyramid:
    @staticmethod
    def build_gaussian_pyramid(img: np.ndarray, levels: int = 3) -> List[np.ndarray]:
        """Builds a multi-scale Gaussian pyramid."""
        pyramid = [img]
        current = img
        for _ in range(levels - 1):
            current = cv2.pyrDown(current)
            pyramid.append(current)
        return pyramid

    @staticmethod
    def match_resolutions(
        img_high_res: np.ndarray, 
        img_low_res: np.ndarray, 
        scale_ratio: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Normalizes two lunar images of disparate ground resolutions (e.g., OHRC 0.25m vs TMC-2 5.0m).
        Downsamples the high-res image with anti-aliasing to bridge the scale domain gap.
        """
        if scale_ratio > 1.2:
            target_w = int(img_high_res.shape[1] / scale_ratio)
            target_h = int(img_high_res.shape[0] / scale_ratio)
            downsampled_high = cv2.resize(
                img_high_res, 
                (target_w, target_h), 
                interpolation=cv2.INTER_AREA
            )
            return downsampled_high, img_low_res
        elif scale_ratio < 0.8:
            inv_scale = 1.0 / scale_ratio
            target_w = int(img_low_res.shape[1] / inv_scale)
            target_h = int(img_low_res.shape[0] / inv_scale)
            downsampled_low = cv2.resize(
                img_low_res, 
                (target_w, target_h), 
                interpolation=cv2.INTER_AREA
            )
            return img_high_res, downsampled_low
        return img_high_res, img_low_res
