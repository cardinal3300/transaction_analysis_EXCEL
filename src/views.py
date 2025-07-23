import logging
from datetime import datetime
# from typing import Literal

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

# Period = Literal["W", "M", "Y", "ALL"]


# def get_transactions_summary(
#     date_str: str,
#     period: Period = "M",
# ) -> dict:
#     """
#     Формирует сводный отчёт по транзакциям за указанный период.
#
#     Аргументы:
#         date_str (str): Базовая дата в формате "YYYY-MM-DD".
#         period (str): Период анализа: W (неделя), M (месяц), Y (год), ALL (всё время).
#
#     Возвращает:
#         dict: Словарь с данными об операциях, курсах валют и котировках акций.
#     """
#     logger.info(f"Формирование отчёта за период '{period}' к дате {date_str}")
#
#     try:
#         current_date = datetime.strptime(date_str, "%Y-%m-%d")
#     except ValueError:
#         logger.error(f"Неверный формат даты: {date_str}")
#         raise
#
#     df = load_transactions()
#
#     # Фильтрация по периоду
#     if period != "ALL":
#         if period == "W":
#             delta = pd.DateOffset(weeks=1)
#         elif period == "M":
#             delta = pd.DateOffset(months=1)
#         elif period == "Y":
#             delta = pd.DateOffset(years=1)
#         else:
#             logger.warning(f"Неизвестный период: {period}")
#             delta = pd.DateOffset(months=1)
#
#         start_date = current_date - delta
#         df = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= current_date)]
#
#     # Суммируем
#     expenses = summarize_expenses(df)
#     income = summarize_income(df)
#
#     # Получаем курсы валют и котировки акций
#     currency_rates = get_currency_rate()
#     stock_prices = get_stock_prices()
#
#     summary = {
#         "Расходы": expenses,
#         "Поступления": income,
#         "Курс валют": currency_rates,
#         "Акции": stock_prices,
#     }
#
#     logger.info(f"Отчёт сформирован: {summary}")
#     return summary


def get_transactions_summary(date_str: str, period: str = "M", df: pd.DataFrame = None) -> dict:
    """
    Возвращает сводную информацию по транзакциям за указанный период.

    Параметры:
        date_str (str): дата в формате 'YYYY-MM-DD'
        period (str): один из вариантов: 'W', 'M', 'Y', 'ALL'

    Возвращает:
        dict: словарь с данными по расходам, доходам, курсам валют и акциям
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
            "Акции": get_stock_prices()
        }

        logger.info("Сводная информация успешно собрана")
        return summary

    except Exception as e:
        logger.exception("Ошибка при формировании сводной информации")
        return {"error": str(e)}
