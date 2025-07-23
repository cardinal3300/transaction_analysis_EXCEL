import json
from datetime import datetime

from src.utils import setup_logger
from src.views import get_transactions_summary

logger = setup_logger(__name__)


def main():
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

        logger.info(f"Формируется отчёт к дате {date_input}")

        summary = get_transactions_summary(date_input)

        print("\n📊 Отчёт по транзакциям:\n")
        print(json.dumps(summary, indent=4, ensure_ascii=False))

    except Exception as e:
        logger.exception(f"Произошла ошибка в приложении: {e}")


if __name__ == "__main__":
    main()
