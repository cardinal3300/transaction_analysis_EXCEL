import pytest
import pandas as pd
from datetime import datetime
from src import utils


@pytest.fixture
def sample_df():
    data = {
        "Дата операции": pd.to_datetime(["2024-07-01", "2024-07-15", "2024-06-20", "2024-01-01"]),
        "Сумма операции": [-100, -250.5, 500, -75],
        "Категория": ["Еда", "Транспорт", "Зарплата", "Наличные"],
    }
    return pd.DataFrame(data)


def test_round_amount():
    assert utils.round_amount(123.6) == 124
    assert utils.round_amount(123.4) == 123


def test_filter_by_date_range_month(sample_df):
    filtered = utils.filter_by_date_range(sample_df, "2024-07-20", "M")
    assert len(filtered) == 2


def test_filter_by_date_range_year(sample_df):
    filtered = utils.filter_by_date_range(sample_df, "2024-07-20", "Y")
    assert len(filtered) == 4


def test_filter_by_date_range_all(sample_df):
    filtered = utils.filter_by_date_range(sample_df, "2024-07-01", "ALL")
    assert len(filtered) == 3


def test_currency_and_stock():
    rates = utils.get_currency_rate()
    stocks = utils.get_stock_prices()
    assert isinstance(rates, dict)
    assert "USD" in rates
    assert isinstance(stocks, dict)
    assert "AAPL" in stocks
