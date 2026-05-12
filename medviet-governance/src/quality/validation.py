# src/quality/validation.py
import pandas as pd


def build_patient_expectation_suite():
    """
    Tạo expectation suite cho patient data.
    Dùng validation thủ công thay vì Great Expectations API 
    (GX v0.17+ có breaking changes với context.sources).
    """
    print("Building patient data validation suite...")
    
    df = pd.read_csv("data/raw/patients_raw.csv")
    checks_passed = 0
    checks_total = 6
    
    # 1. patient_id không được null
    assert df["patient_id"].notna().all(), "patient_id has null values"
    checks_passed += 1
    print(f"  ✓ Check 1: patient_id not null")
    
    # 2. cccd phải có đúng 12 ký tự
    assert (df["cccd"].astype(str).str.len() == 12).all(), "cccd length != 12"
    checks_passed += 1
    print(f"  ✓ Check 2: cccd length == 12")
    
    # 3. ket_qua_xet_nghiem phải trong khoảng [0, 50]
    assert df["ket_qua_xet_nghiem"].between(0, 50).all(), "ket_qua out of range"
    checks_passed += 1
    print(f"  ✓ Check 3: ket_qua_xet_nghiem in [0, 50]")
    
    # 4. benh phải thuộc danh sách hợp lệ
    valid_conditions = ["Tiểu đường", "Huyết áp cao", "Tim mạch", "Khỏe mạnh"]
    assert df["benh"].isin(valid_conditions).all(), "benh has invalid values"
    checks_passed += 1
    print(f"  ✓ Check 4: benh in valid set")
    
    # 5. email phải match regex pattern
    email_regex = r"[^@]+@[^@]+\.[^@]+"
    assert df["email"].astype(str).str.match(email_regex).all(), "email format invalid"
    checks_passed += 1
    print(f"  ✓ Check 5: email format valid")
    
    # 6. Không được có duplicate patient_id
    assert df["patient_id"].is_unique, "patient_id has duplicates"
    checks_passed += 1
    print(f"  ✓ Check 6: patient_id unique")
    
    print(f"\n  All {checks_passed}/{checks_total} checks passed!")
    return {"checks_passed": checks_passed, "checks_total": checks_total}


def validate_anonymized_data(filepath: str) -> dict:
    """
    Validate anonymized data.
    Trả về dict: {"success": bool, "failed_checks": list, "stats": dict}
    """
    df = pd.read_csv(filepath)
    results = {
        "success": True,
        "failed_checks": [],
        "stats": {
            "total_rows": len(df),
            "columns": list(df.columns)
        }
    }

    # Check 1: Không còn CCCD gốc dạng số thuần túy 12 chữ số
    # (sau anonymization, cccd phải là fake — vẫn là 12 số nhưng khác gốc)
    if "cccd" in df.columns:
        original_df = pd.read_csv("data/raw/patients_raw.csv")
        overlap = set(df["cccd"].astype(str)) & set(original_df["cccd"].astype(str))
        if len(overlap) > 0:
            results["success"] = False
            results["failed_checks"].append(
                f"CCCD overlap with original: {len(overlap)} values"
            )

    # Check 2: Không có null values trong các cột quan trọng
    important_cols = ["patient_id", "benh", "ket_qua_xet_nghiem"]
    for col in important_cols:
        if col in df.columns and df[col].isnull().any():
            results["success"] = False
            results["failed_checks"].append(f"Column {col} has null values")

    # Check 3: Số rows phải bằng original
    original_df = pd.read_csv("data/raw/patients_raw.csv")
    if len(df) != len(original_df):
        results["success"] = False
        results["failed_checks"].append(
            f"Row count mismatch: {len(df)} vs {len(original_df)}"
        )

    return results
