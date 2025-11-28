Bajaj Finserv Health Bill Extraction – AI Line-Item Parser (Open-Source)This project is a production-ready OCR + Layout Parsing Pipeline for hospital invoice understanding.It extracts individual bill line-items, quantities, rates, net amounts, and generates:Page-wise extracted line itemsFinal unique line items without double countingTotal reconstructed amount + invoice total reconciliationThe system supports PDF, PNG, and JPG invoices. It automatically converts files, performs OCR, and outputs structured bill JSON. This follows the exact submission format required for the Bajaj Health Datathon.Key FeaturesMulti-page extraction: Handles PDF to page-wise extraction.Robust OCR: Uses EasyOCR with Tesseract fallback.Layout Reconstruction: Reconstructs tables based on bounding boxes.Detailed Extraction: Captures Description, Quantity, Rate, and Amount.Deduplication: Uses fuzzy logic to remove duplicates and prevent double counting.Reconciliation: Automatic invoice total detection and reconciliation.Deployment: Fully deployed API via POST /extract-bill-data.Offline Capability: 100% open-source and runs offline.Tech StackComponentChoiceOCR EngineEasyOCR + Tesseract fallbackLayout UnderstandingBounding-box clustering + Agglomerative column detectionParsingRegex + numeric classification + structured row reconstructionDeduplicationRapidFuzz similarity clusteringAPI ServerFastAPI + UvicornPDF to Imagepdf2imagePreprocessingOpenCV filtersProject Structurebajaj-bill-extractor/
│── app.py                              # FastAPI endpoint entry
│── requirements.txt                    # Dependencies
│── README.md                           # Documentation
│
├── extract_pipeline/
│   ├── main_pipeline.py                # Full extraction logic (final)
│   ├── ocr_backend.py                  # OCR via EasyOCR + Tesseract fallback
│   ├── table_parse.py                  # Row/column parser for line-item extraction
│   ├── table_detection.py              # OCR-box clustering -> rows -> columns
│   ├── postprocess.py                  # Dedup + subtotal/final total matching
│   ├── preprocess.py                   # Denoise / Resize / Threshold
│   ├── utils.py                        # Download + PDF conversion

InstallationThe following steps utilize Anaconda on Windows.Clone the repository:git clone <your repo link>
cd bajaj-bill-extractor
Create and activate the environment:conda create -n bajaj python=3.10 -y
conda activate bajaj
Install dependencies:pip install -r requirements.txt
Note: If using Windows, you must install Tesseract separately. See the Tesseract Wiki for instructions.Run API ServerStart the server using Uvicorn:uvicorn app:app --host 0.0.0.0 --port 8000 --reload
The server will start at: http://localhost:8000/extract-bill-dataAPI UsageCreate an input file (input.json):{
  "document": "[https://hackrx.blob.core.windows.net/assets/datathon-IIT/Sample%20Document%201.pdf?sv=2025-07-05&spr=https&st=2025-11-28T10%3A08%3A01Z&se=2025-11-30T10%3A08%3A00Z&sr=b&sp=r&sig=RSfZaGfX%2Fym%2BQT6BqwjAV6hlI1ehE%2FkTDN4sEAJQoPE%3D](https://hackrx.blob.core.windows.net/assets/datathon-IIT/Sample%20Document%201.pdf?sv=2025-07-05&spr=https&st=2025-11-28T10%3A08%3A01Z&se=2025-11-30T10%3A08%3A00Z&sr=b&sp=r&sig=RSfZaGfX%2Fym%2BQT6BqwjAV6hlI1ehE%2FkTDN4sEAJQoPE%3D)"
}
Execute the request:curl -X POST "http://localhost:8000/extract-bill-data" -H "Content-Type: application/json" -d @input.json
Output (Truncated Sample):{
  "is_success": true,
  "data": {
    "pagewise_line_items": [...],
    "final_line_items": [...],
    "total_item_count": 30,
    "totals": {
      "sum_extracted": 8250.0,
      "invoice_total": 8250.0,
      "diff": 0.0
    }
  }
}
Future ImprovementsFine-tune Donut / LayoutLMv3: To extract tables with higher accuracy (90–98%).Footer/Header Filtering: To remove noisy rows.Fraud Detection: Analysis of font shifts and overwriting.Subtotal Classification: Improved section handling for bonus scoring.AuthorAmit Kumar JhaGitHub: Amitk2457LinkedIn: linkedin.com/in/amit257