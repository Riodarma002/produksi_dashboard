"""
Unit tests for calculation functions
"""
import pytest
import pandas as pd
from datetime import date, datetime

# Add parent directory to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from calculations.production import calc_actuals, calc_achievements, calc_stripping_ratio


class TestCalcActuals:
    """Test cases for calc_actuals function"""

    def test_calc_actuals_normal_case(self):
        """Test normal calculation with valid data"""
        filtered = {
            "ob_f": pd.DataFrame({
                "Volume": [100, 200, 150],
                "Hour LU": ["06", "07", "08"]
            }),
            "ch_f": pd.DataFrame({
                "Netto": [50, 75, 60],
                "Hour LU": ["06", "07", "08"]
            }),
            "ct_f": pd.DataFrame({
                "Production": [30, 40, 35],
                "Hour LU": ["06", "07", "08"]
            })
        }

        result = calc_actuals(filtered)

        assert result["actual_ob"] == 450
        assert result["actual_ch"] == 0.185  # Netto is in kg, divided by 1000
        assert result["actual_ct"] == 105

    def test_calc_actuals_empty_dataframes(self):
        """Test with empty DataFrames"""
        filtered = {
            "ob_f": pd.DataFrame({"Volume": []}),
            "ch_f": pd.DataFrame({"Netto": []}),
            "ct_f": pd.DataFrame({"Production": []})
        }

        result = calc_actuals(filtered)

        assert result["actual_ob"] == 0
        assert result["actual_ch"] == 0
        assert result["actual_ct"] == 0

    def test_calc_actuals_new_format(self):
        """Test new format with Volume column for CH and CT"""
        filtered = {
            "ob_f": pd.DataFrame({
                "Volume": [100, 200, 150],
                "Hour LU": ["06", "07", "08"]
            }),
            "ch_f": pd.DataFrame({
                "Volume": [50, 75, 60],  # New format: Volume in MT
                "Hour LU": ["06", "07", "08"]
            }),
            "ct_f": pd.DataFrame({
                "Volume": [30, 40, 35],  # New format: Volume column
                "Hour LU": ["06", "07", "08"]
            })
        }

        result = calc_actuals(filtered)

        assert result["actual_ob"] == 450
        assert result["actual_ch"] == 185  # No division needed for new format
        assert result["actual_ct"] == 105


class TestCalcAchievements:
    """Test cases for calc_achievements function"""

    def test_calc_achievements_normal_case(self):
        """Test normal achievement calculation"""
        actuals = {"actual_ob": 450, "actual_ch": 185, "actual_ct": 105}
        plans = {
            "plan_ob": 500,
            "plan_ch": 200,
            "plan_ct": 120,
            "has_ct": True
        }

        result = calc_achievements(actuals, plans)

        assert "ach_ob" in result
        assert "ach_ch" in result
        assert "ach_ct" in result
        assert result["ach_ob"] == 90.0  # 450/500*100
        assert result["ach_ch"] == 92.5  # 185/200*100
        assert result["ach_ct"] == 87.5  # 105/120*100

    def test_calc_achievements_zero_plan(self):
        """Test with zero plan values (avoid division by zero)"""
        actuals = {"actual_ob": 100, "actual_ch": 50, "actual_ct": 30}
        plans = {
            "plan_ob": 0,
            "plan_ch": 0,
            "plan_ct": 0,
            "has_ct": True
        }

        result = calc_achievements(actuals, plans)

        # Should handle zero division gracefully by returning 0
        assert result["ach_ob"] == 0
        assert result["ach_ch"] == 0
        assert result["ach_ct"] == 0


class TestCalcStrippingRatio:
    """Test cases for calc_stripping_ratio function"""

    def test_calc_sr_normal_case(self):
        """Test normal stripping ratio calculation"""
        actuals = {"actual_ob": 1000, "actual_ch": 200}
        result = calc_stripping_ratio(actuals)

        expected = 1000 / 200  # SR = OB / Coal
        assert result == expected

    def test_calc_sr_zero_coal(self):
        """Test with zero coal (avoid division by zero)"""
        actuals = {"actual_ob": 1000, "actual_ch": 0}
        result = calc_stripping_ratio(actuals)

        # Should return 0.0 when coal is 0
        assert result == 0.0

    def test_calc_sr_zero_both(self):
        """Test with both zero values"""
        actuals = {"actual_ob": 0, "actual_ch": 0}
        result = calc_stripping_ratio(actuals)

        # Should return 0.0 when both are 0
        assert result == 0.0


class TestConfigValidation:
    """Test cases for config validation"""

    def test_environment_validation(self):
        """Test that environment validation works"""
        from config import validate_environment

        # This should not raise an error if .env is configured
        result = validate_environment()
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
