import pytest
from src.services import investment_bank


@pytest.fixture
def sample_transactions():
    return [
        {"Дата операции": "2024-07-05", "Сумма операции": -143.5},
        {"Дата операции": "2024-07-12", "Сумма операции": -90.0},
        {"Дата операции": "2024-07-15", "Сумма операции": 1000.0},  # доход
        {"Дата операции": "2024-06-20", "Сумма операции": -120.0},  # другой месяц
        {"Дата операции": "2024-07-25", "Сумма операции": -205.0},
    ]


def test_investment_bank(sample_transactions):
    result = investment_bank("2024-07", sample_transactions, 100)
    # Расчёт:
    # -143.5 → +56.5, -90 → +10, -205 → +95 → всего 161.5
    assert result == 161.5
