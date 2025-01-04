import threading
import asyncio
import logging
import json
import os

# Словарь для отслеживания активных потоков
threads = {}

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")

# Функция для выполнения задачи
async def execute_task(script_path):
    try:
        logging.info(f"[EXECUTE_TASK] Начало выполнения скрипта: {script_path}")

        # Проверяем, существует ли скрипт
        if not os.path.exists(script_path):
            logging.error(f"[EXECUTE_TASK] Скрипт не найден: {script_path}")
            return

        # Загружаем скрипт
        with open(script_path, 'r', encoding='utf-8') as file:
            script = json.load(file)

        # Выполняем шаги скрипта
        for step in script.get("steps", []):
            action = step.get("action")
            params = step.get("params", {})
            logging.info(f"[EXECUTE_TASK] Выполнение действия: {action} с параметрами: {params}")
            await asyncio.sleep(1)  # Эмуляция выполнения действия

        logging.info(f"[EXECUTE_TASK] Скрипт успешно завершён: {script_path}")

    except Exception as e:
        logging.error(f"[EXECUTE_TASK] Ошибка выполнения скрипта {script_path}: {e}")

# Запуск задачи в отдельном потоке
def start_task_thread(script_path):
    if script_path in threads and threads[script_path].is_alive():
        logging.warning(f"[START_TASK_THREAD] Задача уже выполняется: {script_path}")
        return

    def task_runner():
        asyncio.run(execute_task(script_path))

    thread = threading.Thread(target=task_runner, daemon=True)
    threads[script_path] = thread
    thread.start()
    logging.info(f"[START_TASK_THREAD] Задача запущена: {script_path}")

# Остановка задачи
def stop_task_thread(script_path):
    thread = threads.get(script_path)
    if thread and thread.is_alive():
        # В реальном проекте нужно предусмотреть корректную остановку asyncio-задачи
        logging.info(f"[STOP_TASK_THREAD] Попытка остановить задачу: {script_path}")
        # Здесь реализовать логику остановки
        threads.pop(script_path, None)
    else:
        logging.warning(f"[STOP_TASK_THREAD] Задача не найдена или уже завершена: {script_path}")

# Остановка всех задач
def stop_all_threads():
    for script_path in list(threads.keys()):
        stop_task_thread(script_path)
    logging.info("[STOP_ALL_THREADS] Все задачи остановлены.")

# Пример использования
if __name__ == "__main__":
    test_script = "test_task.json"

    # Тестовый запуск
    start_task_thread(test_script)
    start_task_thread(test_script)  # Повторный запуск для проверки

    # Ждём выполнения
    import time
    time.sleep(5)

    # Остановка всех задач
    stop_all_threads()
