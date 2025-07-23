import pytest
import pandas as pd
from pathlib import Path
import os
import json
from src.reports import spending_by_workday, save_to_file


@pytest.fixture
def fake_transactions():
    data = {
        "Дата операции": pd.to_datetime(
            [
                "2024-05-13",  # Пн
                "2024-05-14",  # Вт
                "2024-05-18",  # Сб
                "2024-05-19",  # Вс
                "2024-06-10",  # Пн
                "2024-06-15",  # Сб
                "2024-07-01",  # Пн
                "2024-07-06",  # Сб
                "2024-07-07",  # Вс
            ]
        ),
        "Сумма операции": [-100, -200, -300, -400, -150, -250, -120, -130, -140],
    }
    return pd.DataFrame(data)


def test_spending_by_workday_calculations(fake_transactions, tmp_path):
    # Укажем дату — конец анализируемого периода
    result = spending_by_workday(fake_transactions, date="2024-07-10")

    # Проверка, что ключи присутствуют
    assert "Будни" in result
    assert "Выходные" in result

    # Ручной расчёт:
    # Будни: -100, -200, -150, -120 → среднее: 142.5
    # Выходные: -300, -400, -250, -130, -140 → среднее: 244
    assert result["Будни"] == 142
    assert result["Выходные"] == 244


def test_save_to_file_decorator(fake_transactions, tmp_path):
    report_path = tmp_path / "custom_report.json"

    @save_to_file(str(report_path))
    def custom_report(transactions):
        return {"test": 123}

    result = custom_report(fake_transactions)

    # Проверим, что файл создан
    assert report_path.exists()

    # Проверим содержимое файла
    with open(report_path, encoding="utf-8") as f:
        data = json.load(f)

    assert data == {"test": 123}
    assert result == {"test": 123}
