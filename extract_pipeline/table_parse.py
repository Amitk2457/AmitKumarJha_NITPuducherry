# extract_pipeline/table_parse.py
import re
from .ocr_backend import ocr_boxes_from_image
from .table_detection import group_boxes_into_rows, estimate_columns_from_rows, assign_row_to_columns
from rapidfuzz import fuzz

AMOUNT_RE = re.compile(r'([-+]?\d{1,3}(?:[,\s]\d{3})*(?:\.\d{1,2})?)')

def _clean_amount_str(s):
    if s is None or s == "":
        return None
    s = s.replace(",", "").replace(" ", "")
    # sometimes OCR returns leading dots e.g. .00
    s = s.strip()
    try:
        return float(s)
    except:
        # try extract via regex
        m = AMOUNT_RE.findall(s)
        if m:
            try:
                return float(m[-1].replace(",", "").replace(" ", ""))
            except:
                return None
    return None

def parse_page_image(img):
    """
    img: numpy BGR image (preprocessed)
    returns list of line items (dicts)
    """
    boxes = ocr_boxes_from_image(img)
    if not boxes:
        return []

    # group boxes into rows
    rows = group_boxes_into_rows(boxes, y_thresh=12)

    # estimate columns
    col_centers = estimate_columns_from_rows(rows, max_cols=6)

    structured = assign_row_to_columns(rows, col_centers)

    # Heuristic: assume last column is 'net amount', second-last possibly 'discount' or 'rate' etc.
    results = []
    for s in structured:
        cells = s['cells']
        if len(cells) == 0:
            continue

        # Identify numeric-containing columns
        numeric_cols = [i for i,c in enumerate(cells) if AMOUNT_RE.search(c or "")]
        # prefer rightmost numeric as item_amount
        item_amount = None
        item_rate = None
        item_qty = None
        if numeric_cols:
            amt_idx = numeric_cols[-1]
            item_amount = _clean_amount_str(cells[amt_idx])
            # heuristics for qty and rate: look leftwards
            if len(numeric_cols) >= 2:
                # second-rightmost is likely rate or qty
                sec_idx = numeric_cols[-2]
                # guess: if the value looks integer (1,2,3) -> qty else rate
                sec_val = _clean_amount_str(cells[sec_idx])
                if sec_val is not None:
                    if abs(sec_val - round(sec_val)) < 1e-6 and sec_val <= 20:
                        # treat as qty
                        item_qty = float(sec_val)
                    else:
                        item_rate = float(sec_val)
        # Description: everything from leftmost column(s) up to first numeric column
        desc_parts = []
        last_nonempty = -1
        for i,c in enumerate(cells):
            if c and not AMOUNT_RE.search(c):
                desc_parts.append(c)
                last_nonempty = i
            else:
                # stop at first numeric column
                if AMOUNT_RE.search(c):
                    break
        description = " ".join([p for p in desc_parts]).strip()
        if not description:
            # fallback: join entire row but remove numeric pieces
            description = " ".join([c for c in cells if not AMOUNT_RE.search(c or "")]).strip()
            if not description and cells:
                description = cells[0]

        item = {
            "item_name": description,
            "item_amount": round(item_amount,2) if item_amount is not None else None,
            "item_rate": round(item_rate,2) if item_rate is not None else None,
            "item_quantity": item_qty if item_qty is not None else None
        }
        # filter empty noise rows
        if item["item_name"] and (item["item_amount"] is not None):
            results.append(item)
    return results
