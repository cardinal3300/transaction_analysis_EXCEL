import pandas as pd
from functools import wraps
from typing import Optional, Callable
from datetime import datetime, timedelta
import os
from src import setup_logger

logger = setup_logger(__name__)


def save_to_file(filename: Optional[str] = None):
    """
    Декоратор для сохранения результата функции в файл.
    Параметры:
        filename (Optional[str]): Имя файла. Если не указано, создаётся имя по умолчанию.
    Возвращает:
        Callable: Обёрнутая функция с сохранением вывода.
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            try:
                output_file = filename or f"{func.__name__}_output.csv"
                result.to_csv(output_file, index=False)
                logger.info(f"Результат функции '{func.__name__}' сохранён в файл: {output_file}")
            except Exception as e:
                logger.exception(f"Ошибка при сохранении отчёта в файл: {e}")
            return result
        return wrapper
    return decorator


@save_to_file()
def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """
    Вычисляет средние траты в рабочие и выходные дни за последние 3 месяца.
    Параметры:
        transactions (pd.DataFrame): Датафрейм с транзакциями.
        date (Optional[str]): Опорная дата (формат 'YYYY-MM-DD'), по умолчанию — текущая.
    Возвращает:
        pd.DataFrame: Сводка с двумя строками: 'Рабочие дни' и 'Выходные'.
    """

    try:
        logger.info("Вызов функции spending_by_workday")
        logger.debug(f"Размер входного датафрейма: {transactions.shape}")

        if date:
            current_date = datetime.strptime(date, "%Y-%m-%d")
        else:
            current_date = datetime.today()

        logger.info(f"Дата анализа: {current_date.date()}")

        start_date = current_date - timedelta(days=90)
        df_filtered = transactions.copy()
        df_filtered["Дата операции"] = pd.to_datetime(df_filtered["Дата операции"], errors="coerce")
        df_filtered = df_filtered.dropna(subset=["Дата операции", "Сумма операции"])

        df_filtered = df_filtered[
            (df_filtered["Дата операции"] >= start_date) &
            (df_filtered["Дата операции"] <= current_date)
        ]

        logger.info(f"Транзакции в диапазоне: {len(df_filtered)}")

        df_filtered["Тип дня"] = df_filtered["Дата операции"].dt.dayofweek.apply(
            lambda x: "Выходной" if x >= 5 else "Рабочий день"
        )

        grouped = df_filtered.groupby("Тип дня")["Сумма операции"].mean().reset_index()
        grouped.rename(columns={"Сумма операции": "Средние траты"}, inplace=True)
        grouped["Средние траты"] = grouped["Средние траты"].round(2)

        logger.debug(f"Группировка по типу дня:\n{grouped}")
        return grouped

    except Exception as e:
        logger.exception(f"Ошибка в spending_by_workday: {e}")
        return pd.DataFrame(columns=["Тип дня", "Средние траты"])
