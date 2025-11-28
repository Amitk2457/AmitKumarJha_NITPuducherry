# app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from extract_pipeline.main_pipeline import extract_from_document
import uvicorn

app = FastAPI(title="Bajaj Bill Extractor")

class RequestModel(BaseModel):
    document: str  # URL to an image/pdf or local path

@app.post("/extract-bill-data")
async def extract_bill_data(req: RequestModel):
    try:
        result = extract_from_document(req.document)
        return {"is_success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
