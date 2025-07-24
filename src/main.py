import json
from datetime import datetime

import pandas as pd

from src.utils import setup_logger
from src.utils import load_transactions
from src.views import get_transactions_summary
from src.reports import spending_by_workday
from src.services import investment_bank

logger = setup_logger(__name__)


def main():
    """
        Основная точка входа в приложение анализа транзакций.
        Загружает транзакции из Excel-файла, производит фильтрацию по периоду,
        рассчитывает суммарные расходы, поступления, валютные курсы и котировки акций.
        Выводит итоговый отчёт в консоль.
        """

    logger.info("Запуск аналитического приложения по транзакциям.")

    try:
        # Пример входных данных:
        date_input = input("Введите дату (в формате YYYY-MM-DD): ").strip()
        period_input = input("Введите период (W/M/Y/ALL) [по умолчанию M]: ").strip().upper() or "M"

        # Валидация даты
        try:
            datetime.strptime(date_input, "%Y-%m-%d")
        except ValueError:
            logger.error("Неверный формат даты. Используйте YYYY-MM-DD.")
            return
        logger.info(f"Формируется отчёт за период {period_input} к дате {date_input}")

        df = load_transactions("../data/operations.xlsx")

        # Загрузка исходных данных
        logger.info(f"Загружено {len(df)} транзакций.")

        # Отчёт по транзакциям
        summary = get_transactions_summary(date_input, period_input)
        print("\n📊 Отчёт по транзакциям:\n")
        print(json.dumps(summary, indent=4, ensure_ascii=False))

        # Расчёт откладываемой суммы
        month_input = input("Введите год и месяц для расчета откладываемой суммы (в формате YYYY-MM): ").strip()
        savings = investment_bank(month_input, df, limit=100)
        print(f"\n💰 Можно отложить за период: {savings} руб.")

        # Отчёт по рабочим/выходным дням
        weekday_report = spending_by_workday(df, date_input)
        print("\n📅 Средние траты по дням недели за последние 3 месяца:\n")
        print(json.dumps(weekday_report.to_dict(orient="records"), indent=4, ensure_ascii=False))


    except Exception as e:
        logger.exception(f"Произошла ошибка в приложении: {e}")


if __name__ == "__main__":
    main()
