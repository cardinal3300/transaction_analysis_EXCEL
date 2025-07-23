from src.utils import load_transactions
from src.views import analyze_transactions
from src.services import investment_bank
from src.reports import spending_by_workday
import pandas as pd
import json


def main():
    print("🧮 Добро пожаловать в Финансовый Анализатор!\n")
    print("Выберите режим работы:")
    print("1 — Анализ расходов и поступлений")
    print("2 — Расчёт инвесткопилки")
    print("3 — Отчёт по тратам в будни/выходные\n")

    choice = input("Введите номер опции: ").strip()
    transactions = load_transactions("../data/operations.xlsx")

    if choice == "1":
        date = input("Введите дату (YYYY-MM-DD): ").strip()
        range_mode = input("Введите диапазон (W/M/Y/ALL, по умолчанию M): ").strip().upper() or "M"
        result = analyze_transactions(date, range_mode)
        print_json(result)

    elif choice == "2":
        month = input("Введите месяц (YYYY-MM): ").strip()
        limit = input("Введите лимит округления (например, 100): ").strip()
        limit = int(limit) if limit.isdigit() else 100
        tx_list = transactions.to_dict(orient="records")
        result = investment_bank(month, tx_list, limit)
        print(f"\n📥 Можно отложить в инвесткопилку: {result:.2f} руб.\n")

    elif choice == "3":
        date = input("Введите дату (по умолчанию сегодня): ").strip() or None
        result = spending_by_workday(transactions, date)
        print("\n📊 Средние расходы за последние 3 месяца:")
        print(f"Будни:     {result['Будни']} руб.")
        print(f"Выходные:  {result['Выходные']} руб.\n")

    else:
        print("❌ Неизвестная команда. Попробуйте снова.")


def print_json(data: dict):
    print("\n📋 Результат анализа:\n")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    print()


if __name__ == "__main__":
    main()
