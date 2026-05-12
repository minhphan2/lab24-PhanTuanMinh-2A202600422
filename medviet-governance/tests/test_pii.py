# tests/test_pii.py
import pytest
import pandas as pd
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.pii.anonymizer import MedVietAnonymizer

@pytest.fixture(scope="module")
def anonymizer():
    return MedVietAnonymizer()

@pytest.fixture
def sample_df():
    return pd.read_csv("data/raw/patients_raw.csv", dtype=str).head(50)

class TestPIIDetection:

    def test_cccd_detected(self, anonymizer):
        text = "Bệnh nhân Nguyen Van A, CCCD: 012345678901"
        results = anonymizer.analyzer.analyze(text=text, language="en",
                                               entities=["VN_CCCD"])
        assert len(results) >= 1, "CCCD should be detected"

    def test_phone_detected(self, anonymizer):
        text = "Liên hệ: 0912345678"
        results = anonymizer.analyzer.analyze(text=text, language="en",
                                               entities=["VN_PHONE"])
        assert len(results) >= 1, "Phone number should be detected"

    def test_email_detected(self, anonymizer):
        text = "Email: nguyenvana@gmail.com"
        results = anonymizer.analyzer.analyze(text=text, language="en",
                                               entities=["EMAIL_ADDRESS"])
        assert len(results) >= 1, "Email should be detected"

    def test_detection_rate_above_95_percent(self, anonymizer, sample_df):
        """Pipeline phải đạt >95% detection rate trên cccd + phone + email."""
        # Chỉ test cccd, so_dien_thoai, email — các cột regex-based
        # (ho_ten tiếng Việt khó detect bằng en_core_web_sm)
        pii_columns = ["cccd", "so_dien_thoai", "email"]
        rate = anonymizer.calculate_detection_rate(sample_df, pii_columns)
        print(f"\nDetection rate: {rate:.2%}")
        assert rate >= 0.95, f"Detection rate {rate:.2%} < 95%"

class TestAnonymization:

    def test_pii_not_in_output(self, anonymizer, sample_df):
        """Sau anonymization, không còn CCCD gốc trong output."""
        df_anon = anonymizer.anonymize_dataframe(sample_df)
        for original_cccd in sample_df["cccd"]:
            assert str(original_cccd) not in df_anon["cccd"].astype(str).values

    def test_non_pii_columns_unchanged(self, anonymizer, sample_df):
        """Cột benh và ket_qua_xet_nghiem phải giữ nguyên."""
        df_anon = anonymizer.anonymize_dataframe(sample_df)
        assert list(df_anon["benh"]) == list(sample_df["benh"])
        assert list(df_anon["ket_qua_xet_nghiem"]) == list(sample_df["ket_qua_xet_nghiem"])
