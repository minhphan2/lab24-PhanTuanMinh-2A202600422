"""Debug: check detection rate per column."""
import pandas as pd
import sys
sys.path.insert(0, ".")
from src.pii.detector import build_vietnamese_analyzer, detect_pii

analyzer = build_vietnamese_analyzer()
df = pd.read_csv("data/raw/patients_raw.csv", dtype=str).head(10)

for col in ["cccd", "so_dien_thoai", "email"]:
    detected = 0
    total = 0
    for val in df[col].astype(str):
        total += 1
        results = detect_pii(val, analyzer)
        if len(results) > 0:
            detected += 1
        else:
            print(f"  MISSED [{col}]: '{val}'")
    print(f"{col}: {detected}/{total} detected")
    print()
