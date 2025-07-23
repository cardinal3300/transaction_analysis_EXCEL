from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest

from src.utils import filter_transactions_by_period, get_currency_rate, get_stock_prices, round_amount


@pytest.fixture
def sample_df():
    data = {
        "Дата операции": ["2024-05-01", "2024-05-15", "2024-06-01", "2024-06-15", "2024-07-01"],
        "Сумма операции": [100, 200, 300, 400, 500],
    }
    df = pd.DataFrame(data)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"])
    return df


def test_round_amount():
    assert round_amount(123.6) == 124
    assert round_amount(123.4) == 123


def test_filter_by_date_range_month(sample_df):
    date = datetime(2024, 5, 20)
    filtered = filter_transactions_by_period(sample_df, date, "M")
    expected_dates = ["2024-05-01", "2024-05-15"]
    assert all(pd.to_datetime(expected_dates).isin(filtered["Дата операции"]))


def test_filter_by_date_range_year(sample_df):
    date = datetime(2024, 7, 1)
    filtered = filter_transactions_by_period(sample_df, date, "Y")
    assert len(filtered) == 5  # Все попадают в 2024 год


def test_filter_by_date_range_all(sample_df):
    date = datetime(2024, 6, 10)
    filtered = filter_transactions_by_period(sample_df, date, "ALL")
    expected_dates = ["2024-05-01", "2024-05-15", "2024-06-01"]
    assert all(pd.to_datetime(expected_dates).isin(filtered["Дата операции"]))


# === Тест get_currency_rate ===


@patch("src.utils.requests.get")
def test_get_currency_rate_success(mock_get):
    mock_response = {"result": "success", "conversion_rates": {"USD": 90.12, "EUR": 100.45}}
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    result = get_currency_rate(["USD", "EUR"])
    assert isinstance(result, dict)
    assert result["USD"] == 90.12
    assert result["EUR"] == 100.45


@patch("src.utils.requests.get")
def test_get_currency_rate_failure(mock_get):
    mock_get.return_value.status_code = 500

    result = get_currency_rate(["USD", "EUR"])
    assert result == {"USD": None, "EUR": None}


# === Тест get_stock_prices ===


@patch("src.utils.yf.download")
def test_get_stock_prices_success(mock_download):
    import numpy as np
    import pandas as pd

    mock_df = pd.DataFrame({("Close", "AAPL"): [np.nan, 214.39], ("Close", "MSFT"): [np.nan, 300.25]})
    mock_df.columns = pd.MultiIndex.from_tuples(mock_df.columns)

    mock_download.return_value = mock_df

    result = get_stock_prices(["AAPL", "MSFT"])
    assert isinstance(result, dict)
    assert "AAPL" in result and result["AAPL"] == 214.39
    assert "MSFT" in result and result["MSFT"] == 300.25


@patch("src.utils.yf.download")
def test_get_stock_prices_failure(mock_download):
    mock_download.side_effect = Exception("Download error")

    result = get_stock_prices(["AAPL", "MSFT"])
    assert result == {"AAPL": None, "MSFT": None}
