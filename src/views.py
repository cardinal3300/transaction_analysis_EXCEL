import logging
import pandas as pd
from datetime import datetime
from typing import Optional
from src.utils import (
    load_transactions, filter_by_date_range,
    get_currency_rate, get_stock_prices, round_amount
)

logger = logging.getLogger(__name__)


def get_transactions_summary(date_str: str, period: Optional[str] = "M") -> dict:
    """
    Формирует сводку по транзакциям за указанный период до заданной даты.
        Параметры:
            date_str (str): Дата в формате 'YYYY-MM-DD', на которую строится анализ.
            period (str): Диапазон анализа:
                - "W" — неделя;
                - "M" — месяц (по умолчанию);
                - "Y" — год;
                - "ALL" — все транзакции до даты.
        Возвращает:
            dict: JSON-словарь с данными:
                - "Расходы":
                    - "Общая сумма"
                    - "Основные" (7 крупнейших категорий + "Остальное")
                    - "Переводы и наличные"
                - "Поступления":
                    - "Общая сумма"
                    - "Основные" (по категориям)
                - "Курс валют"
                - "Стоимость акций"
        """

    logger.info(f"Анализ транзакций: дата={date_str}, период={period}")

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as e:
        logger.error(f"Неверный формат даты: {e}")
        raise

    df = load_transactions()
    logger.debug(f"Загружено транзакций: {len(df)}")

    df_filtered = filter_by_date_range(df, date, period)
    logger.info(f"Транзакции за выбранный период: {len(df_filtered)}")

    if df_filtered.empty:
        logger.warning("Нет транзакций за указанный период.")
        return {}

    # Разделение по типу
    expenses = df_filtered[df_filtered["Сумма операции"] < 0].copy()
    incomes = df_filtered[df_filtered["Сумма операции"] > 0].copy()
    expenses["Сумма операции"] = expenses["Сумма операции"].abs()

    # Топ-7 расходов
    top_expenses = (
        expenses.groupby("Категория")["Сумма операции"]
        .sum().sort_values(ascending=False)
    )
    top7 = top_expenses[:7].to_dict()
    other_sum = top_expenses[7:].sum()
    if other_sum > 0:
        top7["Остальное"] = round_amount(other_sum)

    # Переводы и наличные
    transfers = expenses[expenses["Категория"].isin(["Переводы", "Наличные"])]
    transfers_sum = (
        transfers.groupby("Категория")["Сумма операции"]
        .sum().sort_values(ascending=False).to_dict()
    )

    # Доходы по категориям
    income_by_category = (
        incomes.groupby("Категория")["Сумма операции"]
        .sum().sort_values(ascending=False).to_dict()
    )

    # Жёстко заданные валюты и акции
    currency_rates = get_currency_rate(base="RUB", targets=["USD", "EUR"])
    stock_prices = get_stock_prices(tickers=["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"])

    result = {
        "Расходы": {
            "Общая сумма": round_amount(expenses["Сумма операции"].sum()),
            "Основные": {k: round_amount(v) for k, v in top7.items()},
            "Переводы и наличные": {k: round_amount(v) for k, v in transfers_sum.items()},
        },
        "Поступления": {
            "Общая сумма": round_amount(incomes["Сумма операции"].sum()),
            "Основные": {k: round_amount(v) for k, v in income_by_category.items()},
        },
        "Курс валют": currency_rates,
        "Акции": stock_prices,
    }

    logger.debug("Результат сформирован.")
    return result
