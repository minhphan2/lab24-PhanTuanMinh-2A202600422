# src/api/main.py
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
from src.access.rbac import get_current_user, require_permission
from src.pii.anonymizer import MedVietAnonymizer

app = FastAPI(title="MedViet Data API", version="1.0.0")
anonymizer = MedVietAnonymizer()

# Resolve data path
_ROOT = Path(__file__).resolve().parent.parent.parent
_RAW_CSV = _ROOT / "data" / "raw" / "patients_raw.csv"

# --- ENDPOINT 1 ---
@app.get("/api/patients/raw")
@require_permission(resource="patient_data", action="read")
async def get_raw_patients(
    current_user: dict = Depends(get_current_user)
):
    """
    Trả về raw patient data (chỉ admin được phép).
    Load từ data/raw/patients_raw.csv
    Trả về 10 records đầu tiên dưới dạng JSON.
    """
    df = pd.read_csv(str(_RAW_CSV), dtype=str)
    return JSONResponse(content=df.head(10).to_dict(orient="records"))

# --- ENDPOINT 2 ---
@app.get("/api/patients/anonymized")
@require_permission(resource="training_data", action="read")
async def get_anonymized_patients(
    current_user: dict = Depends(get_current_user)
):
    """
    Trả về anonymized data (ml_engineer và admin được phép).
    Load raw data → anonymize → trả về JSON.
    """
    df = pd.read_csv(str(_RAW_CSV), dtype=str)
    df_anon = anonymizer.anonymize_dataframe(df.head(10))
    return JSONResponse(content=df_anon.to_dict(orient="records"))

# --- ENDPOINT 3 ---
@app.get("/api/metrics/aggregated")
@require_permission(resource="aggregated_metrics", action="read")
async def get_aggregated_metrics(
    current_user: dict = Depends(get_current_user)
):
    """
    Trả về aggregated metrics (data_analyst, ml_engineer, admin).
    Số bệnh nhân theo từng loại bệnh (không có PII).
    """
    df = pd.read_csv(str(_RAW_CSV), dtype=str)
    metrics = df["benh"].value_counts().to_dict()
    return JSONResponse(content={
        "total_patients": len(df),
        "by_disease": metrics
    })

# --- ENDPOINT 4 ---
@app.delete("/api/patients/{patient_id}")
@require_permission(resource="patient_data", action="delete")
async def delete_patient(
    patient_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Chỉ admin được xóa. Các role khác nhận 403.
    """
    return JSONResponse(content={
        "message": f"Patient {patient_id} deleted",
        "deleted_by": current_user["username"]
    })

@app.get("/health")
async def health():
    return {"status": "ok", "service": "MedViet Data API"}
