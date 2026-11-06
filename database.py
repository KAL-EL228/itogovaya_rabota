import csv
import os
from datetime import datetime


def log_operation(file_path: str, amount: float, from_curr: str, result: float, to_curr: str) -> None:
    """Записывает операцию конвертации в CSV-файл."""
    now = datetime.now().strftime("%H:%M %d.%m.%Y")
    try:
        # Открываем файл на дозапись ('a' - append)
        with open(file_path, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow([now, f"{amount:g}", from_curr, f"{result:.2f}", to_curr])
    except OSError as e:
        print(f"Ошибка при сохранении истории в файл: {e}")


def get_last_operations(file_path: str, count: int) -> list[str]:
    """Возвращает последние count записей из CSV-файла в нужном формате."""
    if not os.path.exists(file_path):
        return []

    operations = []
    try:
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=";")
            for row in reader:
                # Проверяем, что строка не пустая и содержит все 5 элементов
                if len(row) == 5:
                    timestamp, amount, from_curr, result, to_curr = row
                    operations.append(f"{timestamp} {amount} {from_curr} --> {result} {to_curr}")
    except OSError as e:
        print(f"Ошибка при чтении файла истории: {e}")
        return []

    # Возвращаем срез из последних count элементов
    return operations[-count:] if count > 0 else []