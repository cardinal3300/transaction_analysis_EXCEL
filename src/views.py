import logging
from datetime import datetime
from typing import Optional

import pandas as pd

from src.utils import (
    filter_transactions_by_period,
    get_currency_rate,
    get_stock_prices,
    load_transactions,
    summarize_expenses,
    summarize_income,
)

logger = logging.getLogger(__name__)


def get_transactions_summary(date_str: str, period: str = "M", df: Optional[pd.DataFrame] = None) -> dict:
    """
    Возвращает сводную информацию по транзакциям за указанный период.
    Параметры:
        date_str (str): дата в формате 'YYYY-MM-DD'
        period (str): один из вариантов: 'W', 'M', 'Y', 'ALL'
    Возвращает:
        dict: словарь с данными по расходам, доходам, курсам валют и акциям.
    """

    logger.info(f"Сбор сводной информации по дате: {date_str} и периоду: {period}")

    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as e:
        logger.error(f"Ошибка преобразования даты '{date_str}': {e}")
        return {"error": f"Ошибка преобразования даты '{date_str}': {e}"}

    try:
        if df is None:
            df = load_transactions()
        if df.empty:
            logger.warning("Загружены пустые транзакции")
            return {"message": "Нет доступных транзакций"}

        filter_transactions_by_period(df, target_date, period)

        summary = {
            "Расходы": summarize_expenses(df),
            "Поступления": summarize_income(df),
            "Курс валют": get_currency_rate(),
            "Акции": get_stock_prices(),
        }

        logger.info("Сводная информация успешно собрана")
        return summary

    except Exception as e:
        logger.exception("Ошибка при формировании сводной информации")
        return {"error": str(e)}
