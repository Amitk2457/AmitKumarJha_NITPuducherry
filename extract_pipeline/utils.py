# extract_pipeline/utils.py
import os
import requests
from pdf2image import convert_from_path
import tempfile

def download_file(url_or_path, tmpdir):
    if url_or_path.startswith("http://") or url_or_path.startswith("https://"):
        r = requests.get(url_or_path, stream=True, timeout=30)
        r.raise_for_status()
        fname = os.path.join(tmpdir, os.path.basename(url_or_path.split("?")[0]) or "downloaded_doc")
        with open(fname, "wb") as f:
            for chunk in r.iter_content(4096):
                f.write(chunk)
        return fname
    else:
        # local path
        if not os.path.exists(url_or_path):
            raise FileNotFoundError(url_or_path)
        return url_or_path

def pdf_to_images(pdf_path, out_dir):
    # convert pages to PIL images and save to files
    pages = convert_from_path(pdf_path, dpi=300)
    fnames = []
    for i, p in enumerate(pages, start=1):
        ppath = os.path.join(out_dir, f"page_{i:03d}.png")
        p.save(ppath, format="PNG")
        fnames.append(ppath)
    return fnames
