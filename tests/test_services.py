import pytest

from src.services import investment_bank


@pytest.fixture
def transactions_sample():
    return [
        {"Дата операции": "2024-05-03", "Сумма операции": 255.8},
        {"Дата операции": "2024-05-12", "Сумма операции": 78.1},
        {"Дата операции": "2024-05-29", "Сумма операции": 100.0},
        {"Дата операции": "2024-06-01", "Сумма операции": 55.5},  # другая дата, не попадёт
    ]


def test_investment_bank_empty():
    result = investment_bank("2023-12", [], limit=100)
    assert result == 0.0


def test_investment_bank_no_matching_dates(transactions_sample):
    result = investment_bank("2023-01", transactions_sample, limit=100)
    assert result == 0.0
