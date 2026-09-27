import numpy as np
import cv2

def compute_phase_congruency_fast(
    img: np.ndarray, 
    n_scales: int = 3, 
    n_orientations: int = 4, 
    k: float = 2.0, 
    cut_off: float = 0.45
) -> np.ndarray:
    """
    Computes illumination- and shadow-invariant Phase Congruency.
    Based on Kovesi's frequency-domain log-Gabor wavelet model.
    Returns normalized feature map [0, 255] invariant to sun angle & contrast reversal.
    """
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img.copy()

    rows, cols = gray.shape
    # Ensure float32 in [0, 1]
    im_float = gray.astype(np.float32) / 255.0

    # Grid in frequency domain
    u = np.fft.fftfreq(cols)
    v = np.fft.fftfreq(rows)
    u_grid, v_grid = np.meshgrid(u, v)
    
    radius = np.sqrt(u_grid**2 + v_grid**2)
    radius[0, 0] = 1.0 # avoid div by zero at DC
    theta = np.arctan2(-v_grid, u_grid)

    image_fft = np.fft.fft2(im_float)

    total_energy = np.zeros((rows, cols), dtype=np.float32)
    total_amplitude = np.zeros((rows, cols), dtype=np.float32)

    # Multi-scale, multi-orientation log-Gabor filtering
    min_wavelength = 3.0
    mult = 2.1
    sigma_on_f = 0.55
    d_theta_on_sigma = 1.2

    for o in range(n_orientations):
        angl = o * np.pi / n_orientations
        # Angular filter component
        d_theta = np.abs(np.arctan2(
            np.sin(theta - angl), 
            np.cos(theta - angl)
        ))
        spread = np.exp(-(d_theta**2) / (2 * (d_theta_on_sigma * (np.pi / n_orientations))**2))

        for s in range(n_scales):
            wavelength = min_wavelength * (mult ** s)
            fo = 1.0 / wavelength
            # Log-Gabor radial filter
            log_gabor = np.exp(-((np.log(radius / fo))**2) / (2 * (np.log(sigma_on_f))**2))
            log_gabor[0, 0] = 0.0 # zero DC component

            filter_bank = log_gabor * spread

            # Convolve in frequency domain
            filtered_fft = image_fft * filter_bank
            filtered_spatial = np.fft.ifft2(filtered_fft)

            # Even and odd symmetric responses (Real and Imaginary parts)
            e = np.real(filtered_spatial)
            o_resp = np.imag(filtered_spatial)
            amp = np.sqrt(e**2 + o_resp**2)

            total_energy += np.maximum(0.0, amp - k * np.mean(amp))
            total_amplitude += amp

    # Phase congruency = Energy / (Amplitude + epsilon)
    pc = total_energy / (total_amplitude + 1e-4)
    pc = np.clip(pc, 0.0, 1.0)
    
    # Scale to 8-bit image for downstream feature detectors
    pc_uint8 = (pc * 255.0).astype(np.uint8)
    return pc_uint8
