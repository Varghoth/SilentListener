import threading
import asyncio
import logging
import json
import os

from modules.script_actions import ScriptActions

class TaskManager:
    def __init__(self):
        """Инициализация менеджера задач."""
        self.threads = {}  # Словарь для отслеживания активных потоков
        self.actions = ScriptActions()  # Подключаем действия
        logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")

    async def execute_task(self, script_path):
        try:
            logging.info(f"[TaskManager] Выполнение скрипта: {script_path}")

            if not os.path.exists(script_path):
                logging.error(f"[TaskManager] Скрипт не найден: {script_path}")
                return

            with open(script_path, 'r', encoding='utf-8') as file:
                script = json.load(file)

            for block in script.get("blocks", []):
                logging.info(f"[TaskManager] Выполнение блока: {block.get('name', 'Без имени')}")
                for step in block.get("steps", []):
                    action_name = step.get("action")
                    params = step.get("params", {})
                    action = self.actions.get_action(action_name)

                    if action:
                        logging.info(f"[TaskManager] Выполнение действия: {action_name} с параметрами: {params}")
                        await action(params)
                    else:
                        logging.warning(f"[TaskManager] Неизвестное действие: {action_name}")

            logging.info(f"[TaskManager] Скрипт завершён: {script_path}")
        except Exception as e:
            logging.error(f"[TaskManager] Ошибка выполнения скрипта {script_path}: {e}")

    def start_task(self, script_path):
        if script_path in self.threads and self.threads[script_path].is_alive():
            logging.warning(f"[TaskManager] Задача уже выполняется: {script_path}")
            return

        def task_runner():
            asyncio.run(self.execute_task(script_path))

        thread = threading.Thread(target=task_runner, daemon=True)
        self.threads[script_path] = thread
        thread.start()
        logging.info(f"[TaskManager] Задача запущена: {script_path}")

    def stop_task(self, script_path):
        thread = self.threads.get(script_path)
        if thread and thread.is_alive():
            logging.info(f"[TaskManager] Остановка задачи: {script_path}")
            # Реализуйте корректное завершение задачи
            self.threads.pop(script_path, None)
        else:
            logging.warning(f"[TaskManager] Задача не найдена или уже завершена: {script_path}")

    def stop_all_tasks(self):
        """
        Остановка всех задач.
        """
        for script_path in list(self.threads.keys()):
            self.stop_task(script_path)
        logging.info("[STOP_ALL_TASKS] Все задачи остановлены.")

# Пример использования
if __name__ == "__main__":
    manager = TaskManager()
    test_script = "test_task.json"

    # Тестовый запуск
    manager.start_task(test_script)
    manager.start_task(test_script)  # Повторный запуск для проверки

    # Ждём выполнения
    import time
    time.sleep(5)

    # Остановка всех задач
    manager.stop_all_tasks()
