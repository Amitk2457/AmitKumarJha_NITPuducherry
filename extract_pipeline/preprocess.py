# extract_pipeline/preprocess.py
import cv2
import numpy as np

def preprocess_image(path_or_np):
    # Accept both path or numpy image
    if isinstance(path_or_np, str):
        img = cv2.imread(path_or_np)
    else:
        img = path_or_np.copy()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # denoise
    denoised = cv2.GaussianBlur(gray, (3,3), 0)
    # adapt threshold
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 15, 12
    )
    # optional deskew
    coords = cv2.findNonZero(255 - thresh)
    if coords is not None:
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = thresh.shape
        M = cv2.getRotationMatrix2D((w//2, h//2), angle, 1.0)
        thresh = cv2.warpAffine(thresh, M, (w, h),
                                flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        img = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return img
