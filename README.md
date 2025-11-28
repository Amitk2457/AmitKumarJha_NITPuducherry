
# Bajaj Finserv Health Bill Extraction

This project is a **production-ready OCR + Layout Parsing Pipeline for hospital invoice understanding.**  
It extracts individual bill line-items, quantities, rates, net amounts, and generates:

✔ Page-wise extracted line items  
✔ Final unique items without double-counting  
✔ Total reconstructed amount + invoice total reconciliation  

Supports **PDF, PNG, JPG invoices** with **automatic OCR + layout parsing** to produce structured bill JSON.

---

## Key Features

| Feature | Description |
|--------|-------------|
| Multi-page extraction | PDF to page-wise invoice processing |
| Robust OCR | EasyOCR + Tesseract fallback |
| Layout Reconstruction | Bounding box clustering + column detection |
| Detailed Line Parsing | Extracts item, quantity, rate, net total |
| Deduplication | Fuzzy match similarity, removes duplicates |
| Reconciliation | Auto invoice total detection & verification |
| API Deployment | `/extract-bill-data` FastAPI endpoint |
| Offline capability | Fully open-source, runs without internet |

---

## Tech Stack

| Component | Technology |
|----------|-------------|
| OCR Engine | EasyOCR + Tesseract |
| Layout Understanding | Agglomerative Clustering |
| Parsing | Regex + numeric patterns |
| API | FastAPI + Uvicorn |
| Conversion | pdf2image |
| Preprocessing | OpenCV |
| Deduplication | RapidFuzz similarity scoring |

---

## 📁 Project Structure

```
bajaj-bill-extractor/
│── app.py                              # FastAPI endpoint entry
│── requirements.txt                    # Dependencies
│── README.md                           # Documentation
│
├── extract_pipeline/
│   ├── main_pipeline.py                # Full extraction logic (final)
│   ├── ocr_backend.py                  # EasyOCR + Tesseract fallback
│   ├── table_parse.py                  # Table reconstruction & row parsing
│   ├── table_detection.py              # OCR-box clustering & column detection
│   ├── postprocess.py                  # Dedup + reconciliation
│   ├── preprocess.py                   # OpenCV enhancement filters
│   ├── utils.py                        # PDF download & conversion helpers
```

---

## Installation

```
git clone https://github.com/Amitk2457/AmitKumarJha_NITPuducherry.git
cd AmitKumarJha_NITPuducherry

conda create -n bajaj python=3.10 -y
conda activate bajaj

pip install -r requirements.txt
```

> ⚠ Windows users must install **Tesseract OCR** separately.

---

## ▶ Run API Server

```
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

API URL → **https://manual-quadrivalent-unsplenetically.ngrok-free.dev **

---

## API Usage Example

**input.json**
```json
{
  "document": "https://hackrx.blob.core.windows.net/sample.pdf](https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_1.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A21%3A03Z&se=2026-11-25T14%3A21%3A00Z&sr=b&sp=r&sig=2szJobwLVzcVSmg5IPWjRT9k7pHq2Tvifd6seRa2xRI%3D"
}
```

Run request:
```
curl -X POST "https://manual-quadrivalent-unsplenetically.ngrok-free.dev/extract-bill-data" -H "Content-Type: application/json" -d @input.json
```

### 📌 Sample Output
```json
{
  "is_success": true,
  "data": {
    "pagewise_line_items": [...],
    "final_line_items": [...],
    "total_item_count": ...,
    "totals": {
      "sum_extracted": ...,
      "invoice_total": ...,
      "diff": 0.0
    }
  }
}
```

## 👤 Author

**Amit Kumar Jha**  
GitHub: *Amitk2457*  
LinkedIn: *linkedin.com/in/amit257* 🔗

---

⭐ *Open-source & built for Bajaj Health Datathon submissions.*
