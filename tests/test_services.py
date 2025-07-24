import pytest
from src.services import investment_bank


def test_investment_bank_basic():
    transactions = [
        {"Дата операции": "2023-05-10", "Сумма операции": -157.5},
        {"Дата операции": "2023-05-15", "Сумма операции": -290.0},
        {"Дата операции": "2023-05-20", "Сумма операции": 500.0},  # не учитывается
        {"Дата операции": "2023-06-01", "Сумма операции": -120.0},  # другой месяц
    ]
    result = investment_bank("2023-05", transactions, limit=100)
    assert result == 52.5


def test_investment_bank_empty():
    assert investment_bank("2023-05", [], limit=100) == 0.0


def test_investment_bank_invalid_date():
    transactions = [{"Дата операции": "invalid-date", "Сумма операции": -50}]
    assert investment_bank("2023-05", transactions, 100) == 0.0


def test_investment_bank_invalid_month_format():
    with pytest.raises(ValueError):
        investment_bank("2023/05", [], limit=100)
