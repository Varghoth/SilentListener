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
        """
        Запускает выполнение заданий из JSON-скрипта.
        :param script_path: Путь к JSON-скрипту.
        """
        try:
            with open(script_path, "r") as file:
                script = json.load(file)

            while True:  # Циклическое выполнение
                logging.info(f"[TaskManager] Выполнение скрипта: {script_path}")

                for block in script.get("blocks", []):
                    logging.info(f"[TaskManager] Выполнение блока: {block.get('name', 'Unnamed Block')}")
                    
                    for step in block.get("steps", []):
                        action_name = step.get("action")
                        params = step.get("params", {})
                        
                        logging.info(f"[TaskManager] Выполнение действия: {action_name} с параметрами: {params}")
                        action = self.actions.get_action(action_name)
                        
                        if action:
                            await action(params)
                        else:
                            logging.warning(f"[TaskManager] Неизвестное действие: {action_name}")
                
                logging.info("[TaskManager] Завершение текущего цикла выполнения. Ожидание перед перезапуском...")
                await asyncio.sleep(2)  # Небольшая пауза перед новым запуском
        except Exception as e:
            logging.error(f"[TaskManager] Ошибка выполнения скрипта {script_path}: {e}")

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