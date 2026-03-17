"""
Pytest configuration and fixtures
"""
import pytest
import pandas as pd
from datetime import date, datetime


@pytest.fixture
def sample_filtered_data():
    """Sample filtered data for testing"""
    return {
        "ob_f": pd.DataFrame({
            "Volume": [100, 200, 150],
            "Hour LU": ["06", "07", "08"],
            "Date": [date(2026, 3, 15)] * 3
        }),
        "ch_f": pd.DataFrame({
            "Netto": [50, 75, 60],
            "Hour LU": ["06", "07", "08"],
            "Date": [date(2026, 3, 15)] * 3
        }),
        "ct_f": pd.DataFrame({
            "Production": [30, 40, 35],
            "Hour LU": ["06", "07", "08"],
            "Date": [date(2026, 3, 15)] * 3
        }),
        "rain_f": pd.DataFrame({
            "Value": [0, 5, 2],
            "Hour LU": ["06", "07", "08"],
            "Date": [date(2026, 3, 15)] * 3
        })
    }


@pytest.fixture
def sample_plans():
    """Sample plan values for testing"""
    return {
        "plan_ob": 500,
        "plan_ch": 200,
        "plan_ct": 120,
        "has_ct": True
    }
