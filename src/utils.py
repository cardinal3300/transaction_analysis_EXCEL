import os
from datetime import datetime, timedelta
from typing import Dict

import pandas as pd
import requests
import yfinance as yf
from dotenv import load_dotenv

from src import setup_logger

load_dotenv()

api_key = os.getenv("CURRENCY_API_KEY")

logger = setup_logger(__name__)


def load_transactions(filepath: str = "../data/operations.xlsx") -> pd.DataFrame:
    """
    Загружает транзакции из Excel-файла.
    Параметры:
        path (str): Путь к файлу с транзакциями.
    Возвращает:
        pd.DataFrame: Таблица с данными о транзакциях.
    """

    if not os.path.exists(filepath):
        logger.error(f"Файл не найден: {filepath}")
        return pd.DataFrame()

    try:
        df = pd.read_excel(filepath)
        logger.info(f"Файл загружен: {filepath}, {len(df)} записей")
        return df
    except Exception as e:
        logger.exception(f"Ошибка при загрузке Excel-файла: {e}")
        return pd.DataFrame()


def filter_transactions_by_period(df: pd.DataFrame, date: datetime, mode: str = "M") -> pd.DataFrame:
    """
    Фильтрует транзакции по диапазону дат.
    Args:
        df (pd.DataFrame): датафрейм с транзакциями.
        date (str): конечная дата (в формате YYYY-MM-DD).
        mode (str): диапазон ('W', 'M', 'Y', 'ALL').
    Returns:
        pd.DataFrame: отфильтрованные транзакции.
    """

    logger.info(f"Фильтрация по периоду: {mode}, дата: {date.strftime('%Y-%m-%d')}")

    df = df.copy()
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce", dayfirst=True)
    df = df.dropna(subset=["Дата операции"])

    if mode == "W":
        start = date - timedelta(days=date.weekday())
        end = start + timedelta(days=6)
    elif mode == "M":
        start = date.replace(day=1)
        end = date
    elif mode == "Y":
        start = date.replace(month=1, day=1)
        end = date
    elif mode == "ALL":
        end = date
        start = df["Дата операции"].min()
    else:
        logger.warning(f"Неизвестный период: {mode}")
        return pd.DataFrame()

    mask = (df["Дата операции"] >= start) & (df["Дата операции"] <= end)
    result_df = df.loc[mask]
    logger.debug(f"Фильтрация: {len(result_df)} записей между {start} и {end}")
    return result_df


def round_amount(amount: float) -> int:
    """Округляет число до целого."""

    result = round(amount)
    logger.debug(f"Округлено: {amount} → {result}")
    return result


def get_currency_rate(currencies: list = ["RUB", "EUR"], base: str = "USD") -> dict:
    """
    Получает текущие курсы валют с помощью внешнего API.
    Параметры:
        currencies (list): Курсы валют (по умолчанию "USD", "EUR").
        base: (str): Базовая валюта (по умолчанию "RUB")
    Возвращает:
        dict: Словарь с курсами валют или пустой словарь в случае ошибки.
    """

    logger.info(f"Получение курсов валют для: {currencies}, базовая валюта: {base}")

    if not api_key:
        logger.error("API-ключ для ExchangeRate API не найден в .env")
        return {cur: None for cur in currencies}

    try:
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data["result"] != "success":
            logger.error(f"API вернул ошибку: {data}")
            return {cur: None for cur in currencies}

        rates = data["conversion_rates"]
        result = {cur: round(rates.get(cur, 0.0), 2) for cur in currencies}

        for cur, rate in result.items():
            logger.debug(f"{base} → {cur} = {rate}")

        logger.info("Курсы валют успешно получены через API")
        return result

    except requests.RequestException as e:
        logger.exception(f"Ошибка при подключении к ExchangeRate API: {e}")
        return {cur: None for cur in currencies}


def get_stock_prices(tickers: list = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]) -> dict:
    """
    Получает текущие цены акций по тикерам с Yahoo Finance.

    Параметры:
        tickers (list): Список тикеров компаний.

    Возвращает:
        dict: Словарь вида {тикер: цена}, либо None при ошибке.
    """

    prices = {}
    try:
        logger.info(f"Запрос цен акций для: {tickers}")
        stocks = yf.download(
            tickers=tickers, period="1d", interval="1m", progress=False, threads=True, auto_adjust=False
        )
        for ticker in tickers:
            try:
                last_price = stocks["Close"][ticker].dropna().iloc[-1]
                prices[ticker] = round(last_price, 2)
                logger.debug(f"{ticker}: {prices[ticker]}")
            except Exception as e:
                logger.warning(f"Не удалось получить цену для {ticker}: {e}")
                prices[ticker] = None
        logger.info("Цены акций успешно получены")
    except Exception as e:
        logger.exception(f"Ошибка при получении котировок: {e}")
        prices = {t: None for t in tickers}
    return prices


def summarize_expenses(df: pd.DataFrame) -> Dict:
    expenses = df[df["Сумма операции"] < 0].copy()
    total = round(expenses["Сумма операции"].sum() * -1)

    top_categories = (
        expenses.groupby("Категория")["Сумма операции"]
        .sum()
        .sort_values()
        .head(7)
        .abs()
        .round()
        .to_dict()
    )

    other_total = round(total - sum(top_categories.values()))
    if other_total > 0:
        top_categories["Остальное"] = other_total

    cash_transfers = expenses[expenses["Категория"].isin(["Переводы", "Наличные"])]
    transfers_summary = (
        cash_transfers.groupby("Категория")["Сумма операции"]
        .sum()
        .abs()
        .round()
        .to_dict()
    )

    return {
        "Общая сумма": total,
        "Основные": top_categories,
        "Переводы и наличные": transfers_summary,
    }


def summarize_income(df: pd.DataFrame) -> Dict:
    income = df[df["Сумма операции"] > 0].copy()
    total = round(income["Сумма операции"].sum())

    by_category = (
        income.groupby("Категория")["Сумма операции"]
        .sum()
        .sort_values(ascending=False)
        .round()
        .to_dict()
    )

    return {
        "Общая сумма": total,
        "Основные": by_category,
    }
