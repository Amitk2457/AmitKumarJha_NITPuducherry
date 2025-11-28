# extract_pipeline/table_detection.py
import numpy as np
from sklearn.cluster import AgglomerativeClustering
import math

def boxes_to_centers(box):
    x1,y1,x2,y2 = box
    return ((x1+x2)/2.0, (y1+y2)/2.0)

def group_boxes_into_rows(boxes, y_thresh=15):
    """
    boxes: list of {"text","box":[x1,y1,x2,y2],...}
    returns rows: list of lists of boxes sorted left-to-right
    Simple approach: sort by top (y1) and group if center y within y_thresh
    """
    if not boxes:
        return []
    # compute center y for grouping
    for b in boxes:
        x1,y1,x2,y2 = b['box']
        b['cy'] = (y1 + y2) / 2.0
        b['cx'] = (x1 + x2) / 2.0

    # sort by cy
    boxes_sorted = sorted(boxes, key=lambda b: b['cy'])
    rows = []
    current_row = [boxes_sorted[0]]
    for b in boxes_sorted[1:]:
        if abs(b['cy'] - current_row[-1]['cy']) <= y_thresh:
            current_row.append(b)
        else:
            # sort current row left-to-right
            rows.append(sorted(current_row, key=lambda r: r['box'][0]))
            current_row = [b]
    rows.append(sorted(current_row, key=lambda r: r['box'][0]))
    return rows

def estimate_columns_from_rows(rows, max_cols=6):
    """
    Given rows (list of lists of boxes), estimate column boundaries using clustering on box center x.
    returns list of column x positions (centers or boundaries).
    """
    centers = []
    for row in rows:
        for b in row:
            centers.append(b['cx'])
    if not centers:
        return []

    centers_np = np.array(centers).reshape(-1,1)
    # estimate number of clusters using heuristic: unique positions / median row length
    # We'll cluster into up to max_cols clusters
    n_clusters = min(max(2, int(np.median([len(r) for r in rows])) + 1), max_cols)
    # Agglomerative clustering to get stable column centers
    try:
        model = AgglomerativeClustering(n_clusters=n_clusters)
        labels = model.fit_predict(centers_np)
        # compute cluster centers
        clusters = {}
        for i,lab in enumerate(labels):
            clusters.setdefault(lab, []).append(centers[i])
        col_centers = [np.mean(v) for k,v in sorted(clusters.items(), key=lambda kv: np.mean(kv[1]))]
        return col_centers
    except Exception:
        # fallback simple unique sorted centers approx
        uniq = sorted(list(set([round(float(c)) for c in centers])))
        # pick sample if too many
        if len(uniq) > n_clusters:
            step = max(1, len(uniq)//n_clusters)
            uniq = uniq[::step][:n_clusters]
        return [float(x) for x in uniq]

def assign_row_to_columns(rows, col_centers):
    """
    For each row, create a list of text per column by assigning a box to nearest col_center.
    returns structured rows: list of {"cells":[text_by_col], "y": row_y}
    """
    structured = []
    if not col_centers:
        # fallback: return joined row text as single column
        for r in rows:
            structured.append({"cells":[ " ".join([b['text'] for b in r]) ], "y": r[0]['cy']})
        return structured

    for r in rows:
        cells = [[] for _ in col_centers]
        for b in r:
            # find nearest column index
            diffs = [abs(b['cx'] - c) for c in col_centers]
            idx = int(np.argmin(diffs))
            cells[idx].append(b['text'])
        # collapse into strings
        cells_s = [" ".join(c).strip() for c in cells]
        structured.append({"cells": cells_s, "y": r[0]['cy']})
    return structured
