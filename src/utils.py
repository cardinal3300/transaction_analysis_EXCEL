import pandas as pd
from typing import Union
from pathlib import Path
import yfinance as yf
import requests
import os
from dotenv import load_dotenv

load_dotenv()

import logging


def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Консольный обработчик
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        formatter = logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")
        ch.setFormatter(formatter)

        logger.addHandler(ch)
        logger.propagate = False

    return logger


def load_transactions(file_path: Union[str, Path]) -> pd.DataFrame:
    """Загружает Excel-файл с транзакциями.
    Args:
        file_path (str | Path): путь к Excel-файлу.
    Returns:
        pd.DataFrame: таблица с транзакциями."""

    df = pd.read_excel(file_path)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce")
    df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], errors="coerce")
    df = df.dropna(subset=["Дата операции"])  # Удалим записи без даты операции
    return df


def filter_by_date_range(df: pd.DataFrame, end_date: str, mode: str = "M") -> pd.DataFrame:
    """Фильтрует транзакции по диапазону дат.
    Args:
        df (pd.DataFrame): датафрейм с транзакциями.
        end_date (str): конечная дата (в формате YYYY-MM-DD).
        mode (str): диапазон ('W', 'M', 'Y', 'ALL').
    Returns:
        pd.DataFrame: отфильтрованные транзакции."""

    end = pd.to_datetime(end_date)
    if mode == "ALL":
        return df[df["Дата операции"] <= end]
    elif mode == "W":
        start = end - pd.to_timedelta(end.weekday(), unit="D")
    elif mode == "M":
        start = end.replace(day=1)
    elif mode == "Y":
        start = end.replace(month=1, day=1)
    else:
        raise ValueError("Неверный режим диапазона. Используйте W, M, Y или ALL.")
    return df[(df["Дата операции"] >= start) & (df["Дата операции"] <= end)]


def round_amount(amount: float) -> int:
    """Округляет число до целого."""
    return int(round(amount))


def get_currency_rate(base: str = "RUB", symbols: list = ["USD", "EUR"]) -> dict:
    """Получает актуальный курс валют с API exchangerate.host
    Args:
        base (str): базовая валюта (по умолчанию RUB)
        symbols (list): список валют, которые нужны
    Returns:
        dict: словарь с курсами валют."""

    api_key = os.getenv("CURRENCY_API_KEY")
    params = {"base": base, "symbols": ", ".join(symbols)}
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"

    try:
        response = requests.get(url, params=params)
        data = response.json()
        return data.get("rate", {})
    except Exception as e:
        print(f"Ошибка при получении курса валют: {e}")
        return {s: None for s in symbols}


def get_stock_prices(tickers: list = ["AAPL", "MSFT", "GOOGL", "AMZN"]) -> dict:
    """Получает текущие цены акций с помощью Yahoo Finance через yfinance.
    Args:
        tickers (list): тикеры компаний
    Returns:
        dict: {тикер: цена}."""

    prices = {}
    try:
        stocks = yf.download(tickers=tickers, period="1d", interval="1m", progress=False, threads=True)
        for ticker in tickers:
            try:
                last_price = stocks['Close'][ticker].dropna().iloc[-1]
                prices[ticker] = round(last_price, 2)
            except Exception:
                prices[ticker] = None
    except Exception as e:
        print(f"Ошибка при получении котировок: {e}")
        prices = {t: None for t in tickers}

    return prices


# print(get_currency_rate())  # {'USD': 0.0111, 'EUR': 0.0102}
print(get_stock_prices())   # {'AAPL': 187.32, 'MSFT': 412.45, ...}
