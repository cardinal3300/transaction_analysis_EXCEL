from datetime import datetime
from typing import Any, Dict, List

from src import setup_logger

logger = setup_logger(__name__)


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """
    Рассчитывает сумму, которую можно было бы отложить в инвесткопилку за указанный месяц.
    Параметры:
        month (str): Месяц в формате 'YYYY-MM'.
        transactions (List[Dict[str, Any]]): Список транзакций.
        limit (int): Предел округления (например, 100).
    Возвращает:
        float: Сумма накоплений за месяц.
    """

    logger.info(f"Расчёт инвесткопилки за месяц: {month}")
    total_round_sum = 0.0

    try:
        year, mon = map(int, month.split("-"))
    except ValueError:
        logger.error(f"Неверный формат месяца: {month}")
        raise ValueError(f"Неверный формат месяца: '{month}'. Ожидался 'YYYY-MM'.")

    for tx in transactions:
        try:
            tx_date = datetime.strptime(tx["Дата операции"], "%Y.%m.%d.")
        except Exception as e:
            logger.warning(f"Пропущена транзакция из-за ошибки парсинга: {tx} — {e}")
            continue  # пропускаем некорректные даты

        if tx_date.year != year or tx_date.month != mon:
            continue  # не тот месяц

        amount = float(tx.get("Сумма операции", 0))
        if not isinstance(amount, (int, float)) or amount >= 0:
            continue  # только отрицательные суммы — это расходы

         # Вычисление округления вверх до limit
        remainder = abs(amount) % limit
        invest_part = (limit - remainder) if remainder > 0 else 0
        total_round_sum += invest_part

    result = round(total_round_sum, 2)
    logger.info(f"Итого можно было бы отложить: {result} руб.")
    return result
