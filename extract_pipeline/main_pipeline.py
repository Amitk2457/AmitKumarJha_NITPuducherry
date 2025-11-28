# extract_pipeline/main_pipeline.py

import os
import tempfile

from .utils import download_file, pdf_to_images
from .preprocess import preprocess_image
from .table_parse import parse_page_image
from .ocr_backend import ocr_boxes_from_image
from .postprocess import dedupe_items, reconcile_totals


def extract_from_document(document_url_or_path: str):
    """
    Main orchestration function.
    Accepts a URL or local path to an image / PDF and returns structured bill data.

    Returns dict in this shape (wrapped by FastAPI into {"is_success": True, "data": ...}):

    {
        "pagewise_line_items": [
            {
                "page_no": "1",
                "page_type": "Bill Detail",
                "bill_items": [
                    {
                        "item_name": "...",
                        "item_amount": 300.0,
                        "item_rate": 300.0,
                        "item_quantity": 1.0
                    },
                    ...
                ]
            },
            ...
        ],
        "final_line_items": [... deduped across pages ...],
        "total_item_count": 30,
        "totals": {
            "sum_extracted": 8250.0,
            "invoice_total": 8250.0,
            "diff": 0.0
        }
    }
    """
    # temporary directory for downloaded file & PDF pages
    tmpdir = tempfile.mkdtemp(prefix="bill_extract_")

    # 1. Download (or just resolve local) document path
    local_path = download_file(document_url_or_path, tmpdir)

    # 2. Convert PDF to images if needed
    if local_path.lower().endswith(".pdf"):
        page_paths = pdf_to_images(local_path, tmpdir)  # list of PNG paths
    else:
        page_paths = [local_path]

    aggregated_items = []
    pagewise_line_items = []
    pages_texts_for_totals = []

    # 3. Process each page
    for i, page_path in enumerate(page_paths, start=1):
        # 3.1 Preprocess page (deskew, denoise, etc.)
        img = preprocess_image(page_path)  # returns BGR numpy image

        # 3.2 Parse line-items using layout-aware OCR
        page_items = parse_page_image(img)

        # 3.3 Optional: build a big text blob per page to help detect final total
        raw_boxes = ocr_boxes_from_image(img)
        page_text = "\n".join(
            [b["text"] for b in sorted(raw_boxes, key=lambda x: x["box"][1])]
        ) if raw_boxes else ""

        # 3.4 Collect per-page info
        pagewise_line_items.append(
            {
                "page_no": str(i),
                "page_type": "Bill Detail",  # constant for now; can be improved later
                "bill_items": page_items,
            }
        )

        aggregated_items.extend(page_items)
        pages_texts_for_totals.append(page_text)

    # 4. Deduplicate items across all pages to avoid double counting
    final_items = dedupe_items(aggregated_items)

    # 5. Reconcile totals (sum of extracted vs. invoice/printed total if found)
    totals_info = reconcile_totals(final_items, pages_texts_for_totals)

    # 6. Build final response payload
    response = {
        "pagewise_line_items": pagewise_line_items,
        "final_line_items": final_items,
        "total_item_count": len(final_items),
        "totals": totals_info,
    }

    return response
