import os
import pandas as pd
from datetime import datetime
from src.reports import spending_by_workday


def test_spending_by_workday_logic(tmp_path):
    data = {
        "Дата операции": [
            "2024-04-01",  # понедельник
            "2024-04-06",  # суббота
            "2024-04-07",  # воскресенье
            "2024-05-13",  # понедельник
            "2024-06-01",  # суббота
        ],
        "Сумма операции": [100, 150, 100, 300, 50],
    }
    df = pd.DataFrame(data)

    result = spending_by_workday(df, date="2024-07-01")

    assert set(result.columns) == {"Тип дня", "Средние траты"}
    assert "Рабочий день" in result["Тип дня"].values
    assert "Выходной" in result["Тип дня"].values

    # Проверка на осмысленные значения
    values = result.set_index("Тип дня")["Средние траты"].to_dict()
    assert isinstance(values["Рабочий день"], float)
    assert isinstance(values["Выходной"], float)
    assert values["Рабочий день"] > 0
    assert values["Выходной"] > 0


def test_spending_by_workday_saves_file(tmp_path, monkeypatch):
    # Подмена рабочей директории, чтобы не писать в корень проекта
    monkeypatch.chdir(tmp_path)

    data = {
        "Дата операции": ["2024-05-10", "2024-05-11"],
        "Сумма операции": [100, 200],
    }
    df = pd.DataFrame(data)

    spending_by_workday(df, date="2024-07-01")

    # Имя файла, ожидаемое по умолчанию
    expected_file = tmp_path / "spending_by_workday_output.csv"
    assert expected_file.exists()

    # Проверка содержимого
    df_out = pd.read_csv(expected_file)
    assert "Тип дня" in df_out.columns
    assert "Средние траты" in df_out.columns
