# extract_pipeline/postprocess.py
from rapidfuzz import fuzz
import math

def normalize_text(s):
    if not s:
        return ""
    s = s.lower()
    # remove extra punctuation and normalize spaces
    keep = []
    for ch in s:
        if ch.isalnum() or ch.isspace():
            keep.append(ch)
        else:
            keep.append(" ")
    s = "".join(keep)
    s = " ".join(s.split())
    return s.strip()

def dedupe_items(items, name_threshold=85, amount_tol=1.0):
    """
    Cluster items that look duplicates (name fuzzy match + amount near).
    Return merged unique list.
    """
    used = [False]*len(items)
    clusters = []
    for i, it in enumerate(items):
        if used[i]:
            continue
        group = [it]
        used[i] = True
        ni = normalize_text(it.get("item_name",""))
        ai = float(it.get("item_amount") or 0)
        for j in range(i+1, len(items)):
            if used[j]:
                continue
            nj = normalize_text(items[j].get("item_name",""))
            aj = float(items[j].get("item_amount") or 0)
            name_score = fuzz.token_sort_ratio(ni, nj)
            amount_ok = math.isclose(ai, aj, rel_tol=1e-2, abs_tol=amount_tol)
            if name_score >= name_threshold and amount_ok:
                group.append(items[j])
                used[j] = True
        # merge group: choose longest name, keep amount from the most frequent amount in group
        canonical_name = max(group, key=lambda x: len(x.get("item_name",""))).get("item_name")
        amounts = [float(g.get("item_amount") or 0) for g in group]
        # pick median amount
        amounts_sorted = sorted(amounts)
        amt = amounts_sorted[len(amounts_sorted)//2] if amounts_sorted else 0.0
        out = {
            "item_name": canonical_name,
            "item_amount": round(float(amt),2),
            "item_rate": None,
            "item_quantity": None,
            "count": len(group)
        }
        clusters.append(out)
    return clusters

def reconcile_totals(final_items, pages_texts=None):
    """
    final_items: list of items with amounts
    pages_texts: optional list of full-page OCR text strings to find explicit invoice total/subtotal
    """
    sum_extracted = sum([float(it.get("item_amount") or 0) for it in final_items])

    invoice_total = None
    if pages_texts:
        import re
        TOT_RE = re.compile(r'(final\s*total|grand\s*total|total\s*payable|net\s*amount)[\s:]*([0-9\.,]+)', re.I)
        for p in pages_texts:
            for m in TOT_RE.findall(p):
                val = m[1].replace(",", "").strip()
                try:
                    invoice_total = float(val)
                    break
                except:
                    continue
            if invoice_total:
                break

    return {
        "sum_extracted": round(sum_extracted,2),
        "invoice_total": round(invoice_total,2) if invoice_total else None,
        "diff": round((invoice_total - sum_extracted),2) if invoice_total else None
    }
