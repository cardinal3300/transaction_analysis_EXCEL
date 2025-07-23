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

    year, mon = map(int, month.split("-"))
    total_round_sum = 0.0

    for tx in transactions:
        try:
            tx_date = datetime.strptime(tx["Дата операции"], "%Y-%m-%d")
        except Exception:
            continue  # пропускаем некорректные даты
        if tx_date.year != year or tx_date.month != mon:
            continue  # не тот месяц
        amount = tx.get("Сумма операции", 0)
        if amount > 0:
            continue  # нас интересуют только расходы (отрицательные значения)
        # Вычисление округления вверх до limit
        remainder = abs(amount) % limit
        invest_part = (limit - remainder) if remainder != 0 else 0
        total_round_sum += invest_part
    return round(total_round_sum, 2)
