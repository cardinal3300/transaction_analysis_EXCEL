from datetime import datetime, timedelta

import pandas as pd

from src.reports import spending_by_workday


def test_spending_by_workday_logic():
    analysis_date = datetime.strptime("2024-07-01", "%Y-%m-%d")

    data = {
        "Дата операции": [
            (analysis_date - timedelta(days=5)).strftime("%Y-%m-%d"),  # среда (рабочий)
            (analysis_date - timedelta(days=6)).strftime("%Y-%m-%d"),  # вторник (рабочий)
            (analysis_date - timedelta(days=7)).strftime("%Y-%m-%d"),  # понедельник (рабочий)
            (analysis_date - timedelta(days=8)).strftime("%Y-%m-%d"),  # воскресенье (выходной)
        ],
        "Сумма операции": [100, 200, 150, 250],
    }

    df = pd.DataFrame(data)
    result = spending_by_workday(df, date="2024-07-01")

    assert set(result.columns) == {"Тип дня", "Средние траты"}
    assert "Рабочий день" in result["Тип дня"].values
    assert "Выходной" in result["Тип дня"].values

    result_dict = dict(zip(result["Тип дня"], result["Средние траты"]))
    assert result_dict["Рабочий день"] == round((100 + 200 + 150) / 3, 2)  # 150.0
    assert result_dict["Выходной"] == 250.0


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
