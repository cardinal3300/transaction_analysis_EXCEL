from unittest.mock import patch

import pandas as pd
import pytest

from src.views import get_transactions_summary


@pytest.fixture
def mock_transactions():
    return pd.DataFrame(
        [
            {"Дата операции": "2024-07-01", "Сумма операции": -100, "Категория": "Еда"},
            {"Дата операция": "2024-07-02", "Сумма операция": -200, "Категория": "Еда"},
            {"Дата операция": "2024-07-03", "Сумма операция": -300, "Категория": "Транспорт"},
            {"Дата операция": "2024-07-04", "Сумма операция": 1000, "Категория": "Зарплата"},
            {"Дата операция": "2024-07-05", "Сумма операция": -50, "Категория": "Переводы"},
            {"Дата операция": "2024-07-06", "Сумма операция": -30, "Категория": "Наличные"},
        ]
    )


@patch("src.views.load_transactions")
@patch("src.views.get_currency_rate")
@patch("src.views.get_stock_prices")
def test_summary_valid(mock_stocks, mock_rates, mock_load):
    # Мокаем данные о транзакциях
    mock_df = pd.DataFrame(
        [
            {"Дата операции": "2024-07-01", "Сумма операции": 100, "Категория": "Еда"},
            {"Дата операция": "2024-07-02", "Сумма операции": 200, "Категория": "Транспорт"},
            {"Дата операция": "2024-07-03", "Сумма операция": 300, "Категория": "Переводы"},
        ]
    )
    mock_load.return_value = mock_df

    # Мокаем валюту и акции
    mock_rates.return_value = {"USD": 90.0, "EUR": 98.0}
    mock_stocks.return_value = {"AAPL": 190.5, "AMZN": 3200.0}

    result = get_transactions_summary("2024-07-03", "M")

    assert "Расходы" in result
    assert "Поступления" in result
    assert "Курс валют" in result
    assert "Акции" in result


@patch("src.views.load_transactions")
def test_summary_invalid_date(*args):
    result = get_transactions_summary("invalid-date", "M")
    assert "error" in result
    assert "Ошибка преобразования даты" in result["error"]
