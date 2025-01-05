import asyncio
import logging
import json
import os

from modules.script_actions import ScriptActions

class TaskManager:
    def __init__(self, loop):
        self.tasks = {}  # Словарь для отслеживания активных задач
        self.actions = ScriptActions(loop)
        self.loop = loop  # Переданный цикл событий

    async def execute_task(self, script_path, cancel_event):
        try:
            logging.info(f"[TaskManager] Выполнение скрипта: {script_path}")
            if not os.path.exists(script_path):
                logging.error(f"[TaskManager] Скрипт не найден: {script_path}")
                return

            with open(script_path, "r", encoding="utf-8") as file:
                script = json.load(file)

            for block in script.get("blocks", []):
                if cancel_event.is_set():
                    logging.info(f"[TaskManager] Выполнение скрипта {script_path} остановлено.")
                    break

                logging.info(f"[TaskManager] Выполнение блока: {block.get('name', 'Без имени')}")
                for step in block.get("steps", []):
                    if cancel_event.is_set():
                        logging.info(f"[TaskManager] Выполнение остановлено на шаге: {step.get('action')}")
                        break

                    action_name = step.get("action")
                    params = step.get("params", {})
                    action = self.actions.get_action(action_name)

                    if action:
                        logging.info(f"[TaskManager] Выполнение действия: {action_name} с параметрами: {params}")
                        await action(params)
                    else:
                        logging.warning(f"[TaskManager] Неизвестное действие: {action_name}")

            logging.info(f"[TaskManager] Скрипт завершён: {script_path}")
        except asyncio.CancelledError:
            logging.info(f"[TaskManager] Задача {script_path} была отменена.")
        except Exception as e:
            logging.error(f"[TaskManager] Ошибка выполнения скрипта {script_path}: {e}")

    async def start_task(self, script_path):
        if script_path in self.tasks:
            logging.warning(f"[TaskManager] Задача уже выполняется: {script_path}")
            return

        cancel_event = asyncio.Event()
        task = self.loop.create_task(self.execute_task(script_path, cancel_event))
        self.tasks[script_path] = (task, cancel_event)
        logging.info(f"[TaskManager] Задача запущена: {script_path}")

    def stop_task(self, script_path):
        task_tuple = self.tasks.get(script_path)
        if not task_tuple:
            logging.warning(f"[TaskManager] Задача не найдена или уже завершена: {script_path}")
            return

        task, cancel_event = task_tuple
        cancel_event.set()  # Устанавливаем событие отмены
        task.cancel()  # Отменяем задачу
        self.tasks.pop(script_path, None)
        logging.info(f"[TaskManager] Задача остановлена: {script_path}")

    def stop_all_tasks(self):
        for script_path, (task, cancel_event) in list(self.tasks.items()):
            cancel_event.set()
            task.cancel()
        self.tasks.clear()
        logging.info("[TaskManager] Все задачи остановлены.")