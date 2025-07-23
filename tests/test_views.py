import pytest
from unittest.mock import patch
import pandas as pd
from src.views import get_transactions_summary

@pytest.fixture
def mock_transactions():
    return pd.DataFrame([
        {"Дата операции": "2024-07-01", "Сумма операции": -100, "Категория": "Еда"},
        {"Дата операция": "2024-07-02", "Сумма операция": -200, "Категория": "Еда"},
        {"Дата операция": "2024-07-03", "Сумма операция": -300, "Категория": "Транспорт"},
        {"Дата операция": "2024-07-04", "Сумма операция": 1000, "Категория": "Зарплата"},
        {"Дата операция": "2024-07-05", "Сумма операция": -50, "Категория": "Переводы"},
        {"Дата операция": "2024-07-06", "Сумма операция": -30, "Категория": "Наличные"},
    ])

@patch("src.views.load_transactions")
@patch("src.views.get_currency_rate")
@patch("src.views.get_stock_prices")
def test_summary_valid(mock_stocks, mock_rates, mock_load, mock_transactions):
    df = mock_transactions
    df.columns = ["Дата операции", "Сумма операции", "Категория"]
    mock_load.return_value = df
    mock_rates.return_value = {"USD": 90.0, "EUR": 100.0}
    mock_stocks.return_value = {"AAPL": 200.0, "MSFT": 300.0}

    result = get_transactions_summary("2024-07-06", period="M")

    assert isinstance(result, dict)
    assert result["Расходы"]["Общая сумма"] == 680
    assert result["Поступления"]["Общая сумма"] == 1000
    assert result["Курс валют"] == {"USD": 90.0, "EUR": 100.0}
    assert result["Акции"] == {"AAPL": 200.0, "MSFT": 300.0}


@patch("src.views.load_transactions")
@patch("src.views.get_currency_rate", return_value={})
@patch("src.views.get_stock_prices", return_value={})
def test_summary_empty_transactions(mock_stocks, mock_rates, mock_load):
    # Пустой DataFrame с нужными колонками
    mock_load.return_value = pd.DataFrame(columns=["Дата операции", "Сумма операции", "Категория"])
    result = get_transactions_summary("2024-07-06", period="M")
    assert result["Расходы"]["Общая сумма"] == 0
    assert result["Поступления"]["Общая сумма"] == 0


@patch("src.views.load_transactions", return_value=pd.DataFrame(columns=["Дата операции", "Сумма операции", "Категория"]))
def test_summary_invalid_date(mock_load):
    with pytest.raises(ValueError):
        get_transactions_summary("invalid-date", period="M")


@patch("src.views.load_transactions", return_value=pd.DataFrame(columns=["Дата операции", "Сумма операции", "Категория"]))
@patch("src.views.get_currency_rate", side_effect=Exception("API fail"))
@patch("src.views.get_stock_prices", side_effect=Exception("Stocks fail"))
def test_summary_api_fail(mock_stocks, mock_rates, mock_load):
    result = get_transactions_summary("2024-07-06", period="ALL")
    assert result["Курс валют"] == {}
    assert result["Акции"] == {}