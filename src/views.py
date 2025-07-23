from typing import Optional, Literal
import pandas as pd
from src.utils import (
    load_transactions,
    filter_by_date_range,
    round_amount,
    get_currency_rate,
    get_stock_prices,
    setup_logger,
)

logger = setup_logger(__name__)

Range = Literal["W", "M", "Y", "ALL"]


def analyze_transactions(date: str, range_mode: Optional[Range] = "M") -> dict:

    df = load_transactions("data/operations.xlsx")
    filtered = filter_by_date_range(df, date, range_mode)

    # Расходы (только отрицательные суммы)
    expenses = filtered[filtered["Сумма операции"] < 0]
    total_expenses = round_amount(abs(expenses["Сумма операции"].sum()))

    # Поступления (положительные суммы)
    income = filtered[filtered["Сумма операции"] > 0]
    total_income = round_amount(income["Сумма операции"].sum())

    # --- Топ-7 категорий расходов ---
    expense_by_category = expenses.groupby("Категория")["Сумма операции"].sum().abs().sort_values(ascending=False)

    top_expense = expense_by_category.head(7).to_dict()
    if len(expense_by_category) > 7:
        other_sum = expense_by_category.iloc[7:].sum()
        top_expense["Остальное"] = round_amount(other_sum)

    top_expense = {k: round_amount(v) for k, v in top_expense.items()}

    # --- Переводы и наличные ---
    transfers = expenses[expenses["Категория"].isin(["Переводы", "Наличные"])]
    transfer_sum = (
        transfers.groupby("Категория")["Сумма операции"]
        .sum()
        .abs()
        .sort_values(ascending=False)
        .apply(round_amount)
        .to_dict()
    )

    # --- Доходы по категориям ---
    income_by_category = (
        income.groupby("Категория")["Сумма операции"].sum().sort_values(ascending=False).apply(round_amount).to_dict()
    )

    return {
        "Расходы": {"Общая сумма": total_expenses, "Основные": top_expense, "Переводы и наличные": transfer_sum},
        "Поступления": {"Общая сумма": total_income, "Основные": income_by_category},
        "Курс валют": get_currency_rate(),
        "Стоимость акций": get_stock_prices(),
    }
