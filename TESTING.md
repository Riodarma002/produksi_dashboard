# Testing Guide

## Overview
This project uses **pytest** for unit testing. Test files are located in the `tests/` directory.

## Running Tests

### Run all tests:
```bash
pytest tests/
```

### Run with coverage report:
```bash
pytest tests/ --cov=. --cov-report=html
```

### Run specific test file:
```bash
pytest tests/test_calculations.py -v
```

### Run specific test class:
```bash
pytest tests/test_calculations.py::TestCalcActuals -v
```

### Run specific test function:
```bash
pytest tests/test_calculations.py::TestCalcActuals::test_calc_actuals_normal_case -v
```

## Test Structure

```
tests/
├── __init__.py           # Test package initialization
├── conftest.py           # Shared fixtures
├── test_calculations.py  # Tests for calculation functions
└── test_logger.py        # Tests for logger utility
```

## Writing New Tests

1. Create a new test file in `tests/` directory
2. Import required modules and fixtures
3. Use descriptive test names: `test_<function>_<scenario>`
4. Use pytest fixtures for common test data

Example:
```python
def test_my_function_normal_case():
    result = my_function(input_data)
    assert result == expected_output
```

## Fixtures

Shared fixtures are defined in `conftest.py`:
- `sample_filtered_data`: Sample production data
- `sample_plans`: Sample plan values

Use them in your tests:
```python
def test_with_fixture(sample_filtered_data):
    result = calc_actuals(sample_filtered_data)
    assert result is not None
```

## CI/CD Integration

To run tests in CI/CD pipeline:
```yaml
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest tests/ --cov=. --cov-fail-under=80
```
