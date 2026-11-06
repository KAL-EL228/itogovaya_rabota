from main import (
    convert_currency,
    save_rates_to_cache,
    load_rates_from_cache,
    history_file,
    cache_file,
)
from database import log_operation, get_last_operations


def run_all_tests():
    print("==========================================")
    print("   ЗАПУСК ТЕСТИРОВАНИЯ ОСНОВНЫХ ФУНКЦИЙ   ")
    print("==========================================")

    # Тестовые курсы для проверки расчетов
    test_rates = {"RUB": 1.0, "USD": 90.0, "EUR": 100.0}

    """ТЕСТ 1: Математика конвертации """
    print("\n[Тест 1] Проверка функции convert_currency:")
    res_usd = convert_currency(9000, "RUB", "USD", test_rates)
    print(f"  -> Конвертация 9000 RUB в USD (по курсу 90): получено {res_usd} USD (ожидалось 100.0)")
    assert res_usd == 100.0, "Ошибка в расчете RUB -> USD"

    res_rub = convert_currency(50, "EUR", "RUB", test_rates)
    print(f"  -> Конвертация 50 EUR в RUB (по курсу 100): получено {res_rub} RUB (ожидалось 5000.0)")
    assert res_rub == 5000.0, "Ошибка в расчете EUR -> RUB"
    print("  [OK] Математика работает верно!")

    """ТЕСТ 2: Обработка исключени"""
    print("\n[Тест 2] Проверка перехвата исключений (ошибок):")
    try:
        convert_currency(-100, "RUB", "USD", test_rates)
        assert False, "Должна была возникнуть ошибка ValueError"
    except ValueError as e:
        print(f"  -> Успешно перехвачена ошибка отрицательной суммы: '{e}'")

    try:
        convert_currency(100, "RUB", "GBP", test_rates)
        assert False, "Должна была возникнуть ошибка KeyError"
    except KeyError as e:
        print(f"  -> Успешно перехвачена ошибка неизвестной валюты: {e}")
    print("  [OK] Исключения отрабатывают штатно!")

    """ТЕСТ 3: Кэширование курсов"""
    print(f"\n[Тест 3] Проверка сохранения и чтения кэша ({cache_file}):")
    save_rates_to_cache(test_rates, cache_file)
    loaded = load_rates_from_cache(cache_file)
    print(f"  -> Записано в файл кэша: {test_rates}")
    print(f"  -> Прочитано из файла кэша: {loaded}")
    assert loaded == test_rates, "Данные кэша не совпадают"
    print("  [OK] Кэширование работает исправно!")

    """ТЕСТ 4: Запись в реальную БД (history.csv) и чтение из нее"""
    print(f"\n[Тест 4] Проверка записи и чтения БД истории ({history_file}):")
    log_operation(history_file, 9000, "RUB", res_usd, "USD")
    log_operation(history_file, 50, "EUR", res_rub, "RUB")
    print(f"  -> В файл '{history_file}' добавлены 2 тестовые записи.")

    last_ops = get_last_operations(history_file, 2)
    print("  -> Читаем последние 2 записи напрямую из БД:")
    for op in last_ops:
        print(f"     {op}")

    assert len(last_ops) >= 2, "Записи не сохранились в историю"
    assert "9000 RUB --> 100.00 USD" in last_ops[-2], "Неверный формат первой записи"
    assert "50 EUR --> 5000.00 RUB" in last_ops[-1], "Неверный формат второй записи"
    print("  [OK] Запись и чтение БД истории прошли успешно!")

    print("\n==========================================")
    print(" ИТОГ: ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ! ")
    print("==========================================")


if __name__ == "__main__":
    run_all_tests()