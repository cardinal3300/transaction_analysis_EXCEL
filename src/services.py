from typing import Any, Hashable

from pandas import to_datetime

from src import setup_logger

logger = setup_logger(__name__)


def investment_bank(month: str, transactions: list[dict[Hashable, Any]], limit: int) -> float:
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
            raw_date = tx["Дата операции"]

            if "." in raw_date or ":" in raw_date:
                tx_date = to_datetime(tx["Дата операции"], dayfirst=True, errors="raise")
            else:
                tx_date = to_datetime(tx["Дата операции"], dayfirst=False, errors="raise")
        except Exception as e:
            logger.warning(f"Пропущена транзакция из-за ошибки парсинга: {tx} — {e}")
            continue  # пропускаем некорректные даты

        if tx_date.year != year or tx_date.month != mon:
            continue  # не тот месяц

        amount = tx.get("Сумма операции", 0)
        if amount >= 0:
            continue  # только отрицательные суммы — это расходы

        # Вычисление округления вверх до limit
        remainder = abs(amount) % limit
        invest_part = (limit - remainder) if remainder > 0 else 0
        total_round_sum += invest_part

    result = round(total_round_sum, 2)
    logger.info(f"Итого можно было бы отложить: {result} руб.")
    return result
