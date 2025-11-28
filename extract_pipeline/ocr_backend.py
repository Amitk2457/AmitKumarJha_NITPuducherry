# extract_pipeline/ocr_backend.py
import easyocr
import pytesseract
import numpy as np
from PIL import Image
import cv2

# Initialize EasyOCR reader once; set gpu=True if you have GPU and proper torch
_reader = easyocr.Reader(['en'], gpu=False)

def image_to_pil(img):
    """Accept numpy BGR or PIL and return PIL RGB"""
    if isinstance(img, np.ndarray):
        return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    return img

def ocr_boxes_from_image(image):
    """
    Returns list of dicts:
      [{"text": "...", "box": [x1,y1,x2,y2]}, ...]
    Uses EasyOCR for detection+recognition and falls back to pytesseract if needed.
    """
    pil = image_to_pil(image)
    np_img = np.array(pil)  # RGB
    # EasyOCR returns list of (bbox, text, confidence)
    try:
        results = _reader.readtext(np_img, detail=1, paragraph=False)
        boxes = []
        for bbox, text, conf in results:
            # bbox: 4 points [[x,y],...]
            xs = [int(p[0]) for p in bbox]
            ys = [int(p[1]) for p in bbox]
            x1, x2 = min(xs), max(xs)
            y1, y2 = min(ys), max(ys)
            boxes.append({"text": text.strip(), "box": [x1, y1, x2, y2], "conf": float(conf)})
        if len(boxes) > 0:
            return boxes
    except Exception:
        pass

    # Fallback: pytesseract single-line boxes
    try:
        data = pytesseract.image_to_data(pil, output_type=pytesseract.Output.DICT)
        boxes = []
        n = len(data['level'])
        for i in range(n):
            txt = data['text'][i].strip()
            if not txt:
                continue
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            boxes.append({"text": txt, "box": [x, y, x + w, y + h], "conf": float(data['conf'][i]) if data['conf'][i] != '-1' else 0.0})
        return boxes
    except Exception:
        return []
