import pytest
import pandas as pd
from unittest.mock import patch
from src.views import analyze_transactions


@pytest.fixture
def fake_df():
    data = {
        "Дата операции": pd.to_datetime(
            [
                "2024-07-01",
                "2024-07-05",
                "2024-07-10",
                "2024-07-12",
                "2024-07-15",
                "2024-07-18",
                "2024-07-20",
                "2024-07-21",
                "2024-07-25",
            ]
        ),
        "Сумма операции": [-100, -250, -50, -75, -30, 500, 300, 200, -40],  # расходы  # доходы  # перевод
        "Категория": ["Еда", "Транспорт", "Еда", "Развлечения", "Кафе", "Зарплата", "Фриланс", "Подарки", "Переводы"],
    }
    return pd.DataFrame(data)


@patch("src.views.load_transactions")
def test_analyze_transactions(mock_load, fake_df):
    mock_load.return_value = fake_df

    result = analyze_transactions("2024-07-22", "M")

    # Проверим основные ключи
    assert "Расходы" in result
    assert "Поступления" in result
    assert "Курс валют" in result
    assert "Стоимость акций" in result

    # Расходы: суммы < 0 → [-100, -250, -50, -75, -30, -40] → сумма: 545
    assert result["Расходы"]["Общая сумма"] == 545

    # Поступления: [500, 300, 200] → сумма: 1000
    assert result["Поступления"]["Общая сумма"] == 1000

    # Категории должны быть округлены
    for val in result["Расходы"]["Основные"].values():
        assert isinstance(val, int)

    for val in result["Поступления"]["Основные"].values():
        assert isinstance(val, int)

    # Переводы и наличные
    assert "Переводы" in result["Расходы"]["Переводы и наличные"]
    assert result["Расходы"]["Переводы и наличные"]["Переводы"] == 40
