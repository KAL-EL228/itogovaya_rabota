import os
import json
import requests
from dotenv import load_dotenv
from database import log_operation, get_last_operations

# Загружаем переменные окружения из .env
load_dotenv()

history_file = os.getenv("history_file", "history.csv")
cache_file = os.getenv("cache_file", "rates_cache.json")
api = os.getenv("api", "https://www.cbr-xml-daily.ru/daily_json.js")

def save_rates_to_cache(rates: dict, cache_file: str) -> None:
    """Сохраняет словарь курсов валют в JSON-файл кэша."""
    try:
        with open(cache_file, mode="w", encoding="utf-8") as file:
            json.dump(rates, file, ensure_ascii=False, indent=4)
    except OSError as e:
        print(f"Предупреждение: не удалось обновить кэш курсов: {e}")


def load_rates_from_cache(cache_file: str) -> dict | None:
    """Загружает курсы валют из JSON-файла кэша."""
    if not os.path.exists(cache_file):
        return None
    try:
        with open(cache_file, mode="r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Ошибка чтения файла кэша: {e}")
        return None


def get_exchange_rates(api: str, cache_file: str) -> dict | None:
    """Получает актуальные курсы через API или возвращает их из кэша при отсутствии сети."""
    try:
        response = requests.get(api, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        rates = {
            "RUB": 1.0,
            "USD": float(data["Valute"]["USD"]["Value"]),
            "EUR": float(data["Valute"]["EUR"]["Value"])
        }
        save_rates_to_cache(rates, cache_file)
        return rates
    except (requests.RequestException, KeyError, ValueError):
        print("\n[!] Нет доступа к сети или API недоступен. Пробуем загрузить курсы из кэша...")
        cached_rates = load_rates_from_cache(cache_file)
        if cached_rates:
            print("[i] Используются сохраненные курсы из кэша.")
            return cached_rates
        print("[Х] Ошибка: кэш отсутствует. Проверьте подключение к интернету.")
        return None


def convert_currency(amount: float, from_curr: str, to_curr: str, rates: dict) -> float:
    """Конвертирует сумму из одной валюты в другую по переданным курсам."""
    if amount < 0:
        raise ValueError("Сумма для конвертации не может быть отрицательной.")
    if from_curr not in rates or to_curr not in rates:
        raise KeyError("Выбрана неподдерживаемая валюта.")
    
    # Переводим исходную валюту в рубли и делим на курс целевой валюты
    amount_in_rub = amount * rates[from_curr]
    return round(amount_in_rub / rates[to_curr], 2)


def select_currency(prompt_text: str) -> str | None:
    """Функция для выбора валюты по цифре"""
    currencies = {"1": "RUB", "2": "USD", "3": "EUR"}
    print(f"\n{prompt_text}")
    print("1 - RUB\n2 - USD\n3 - EUR")
    choice = input("Ваш выбор (1-3): ").strip()
    return currencies.get(choice)


def handle_conversion_menu():
    """Вкладка 1: Полный цикл конвертации валют с записью в историю."""
    print("\n--- КОНВЕРТАЦИЯ ВАЛЮТ ---")
    
    # 1. Выбираем исходную валюту
    from_curr = select_currency("Какую валюту вы хотите конвертировать?")
    if not from_curr:
        print("Ошибка: неверный выбор валюты. Нужно ввести 1, 2 или 3.")
        return

    # 2. Вводим и проверяем сумму
    amount_str = input(f"Введите сумму в {from_curr}: ").strip().replace(",", ".")
    try:
        amount = float(amount_str)
        if amount <= 0:
            print("Ошибка: сумма должна быть больше нуля.")
            return
    except ValueError:
        print("Ошибка: введено некорректное число.")
        return

    # 3. Выбираем целевую валюту
    to_curr = select_currency("В какую валюту необходимо конвертировать?")
    if not to_curr:
        print("Ошибка: неверный выбор целевой валюты. Нужно ввести 1, 2 или 3.")
        return

    # 4. Получаем курсы (из API или кэша)
    rates = get_exchange_rates(api, cache_file)
    if not rates:
        return

    # 5. Считаем и записываем в историю
    try:
        result = convert_currency(amount, from_curr, to_curr, rates)
        print(f"\nРезультат: {amount:g} {from_curr} --> {result:.2f} {to_curr}")
        
        # Записываем успешную операцию в CSV-файл истории!
        log_operation(history_file, amount, from_curr, result, to_curr)
    except (ValueError, KeyError) as e:
        print(f"Ошибка при расчете: {e}")


def handle_history_menu():
    """Вкладка 2: Вывод последних N операций из истории."""
    print("\n--- ИСТОРИЯ КОНВЕРТАЦИЙ ---")
    user_input = input("Сколько последних операций вывести? Введите число: ").strip()
    
    try:
        count = int(user_input)
        if count <= 0:
            print("Ошибка: число должно быть больше нуля.")
            return
    except ValueError:
        print("Ошибка: необходимо ввести целое число (например, 10).")
        return

    history = get_last_operations(history_file, count)
    
    if not history:
        print("История операций пока пуста.")
    else:
        print(f"\nПоследние операции (показано {len(history)}):")
        for record in history:
            print(record)


def main(): 
    """Цикл консольного интерфейса."""
    while True:
        print("\n=== КОНВЕРТЕР ВАЛЮТ ===")
        print("1 - Конвертация")
        print("2 - История конвертаций")
        print("3 - Выход из программы")
        
        choice = input("Выберите действие (1-3): ").strip()
        
        if choice == "1":
            handle_conversion_menu()
        elif choice == "2":
            handle_history_menu()
        elif choice == "3":
            print("Выход из программы.")
            break
        else:
            print("Ошибка: неверный ввод. Пожалуйста, введите цифру 1, 2 или 3.")


if __name__ == "__main__":
    main()