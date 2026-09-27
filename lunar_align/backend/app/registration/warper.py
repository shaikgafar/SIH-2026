import cv2
import numpy as np
import base64
from typing import Tuple, Dict

def ndarray_to_base64_png(img: np.ndarray) -> str:
    """Encodes a uint8 image into a base64 data URI string."""
    if len(img.shape) == 2:
        # Grayscale to RGB for web display
        display_img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    else:
        display_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
    _, buffer = cv2.imencode('.png', display_img)
    b64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/png;base64,{b64}"

class ImageWarper:
    @staticmethod
    def warp_and_blend(
        img1: np.ndarray, 
        img2: np.ndarray, 
        H: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """
        Warps img2 into img1's coordinate system using Homography H.
        Generates warped image, difference heatmap, and blended overlay.
        """
        h1, w1 = img1.shape[:2]
        
        # Warp Image 2 into Image 1 coordinate space
        # Note: If H maps img1 -> img2, we invert it (or apply direct depending on convention)
        try:
            H_inv = np.linalg.inv(H)
        except Exception:
            H_inv = H

        warped_img2 = cv2.warpPerspective(
            img2, 
            H_inv, 
            (w1, h1), 
            borderMode=cv2.BORDER_CONSTANT, 
            borderValue=0
        )

        # Difference heatmap (aligned craters should yield minimal difference)
        valid_mask = warped_img2 > 0
        diff = cv2.absdiff(img1, warped_img2)
        diff[~valid_mask] = 0
        diff_color = cv2.applyColorMap(diff, cv2.COLORMAP_JET)
        diff_color[~valid_mask] = [15, 23, 42] # match background dark color

        # 50/50 Blended overlay
        overlay = np.zeros((h1, w1, 3), dtype=np.uint8)
        # Put img1 in Green channel, warped img2 in Red/Magenta channel
        # Coincident crater rims turn Yellow/White!
        overlay[:, :, 0] = warped_img2 # Blue
        overlay[:, :, 1] = img1        # Green
        overlay[:, :, 2] = warped_img2 # Red (Magenta + Green = aligned composite)

        return {
            "warped": warped_img2,
            "difference": diff_color,
            "overlay": overlay
        }
