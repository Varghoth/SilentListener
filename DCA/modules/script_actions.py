import subprocess
import logging
import asyncio
import pyautogui
import time
import cv2
import numpy as np
import pyautogui
import threading

from global_storage import get_full_path
from modules.screen_service import ScreenService
from modules.mouse_service import MouseController

class ScriptActions:
    def __init__(self, loop):
        self.loop = loop
        self.actions = {
            "log_message": self.log_message_action,
            "wait": self.wait_action,
            "capture_screen": self.capture_screen_action,
            "find_template": self.find_template_action,
            "click_template": self.click_template_action,
        }

    async def log_message_action(self, params):
        try:
            message = params.get("message", "Нет сообщения")
            logging.info(f"[LOG_MESSAGE_ACTION] Сообщение: {message}")
        except Exception as e:
            logging.error(f"[LOG_MESSAGE_ACTION] Ошибка: {e}")

    async def wait_action(self, params):
        try:
            duration = params.get("duration", 0)
            logging.info(f"[WAIT_ACTION] Задержка {duration} секунд.")
            await asyncio.sleep(duration)  # Убедитесь, что sleep выполняется в правильном цикле
            logging.info("[WAIT_ACTION] Задержка завершена.")
        except asyncio.CancelledError:
            logging.info("[WAIT_ACTION] Задержка отменена.")
        except Exception as e:
            logging.error(f"[WAIT_ACTION] Ошибка: {e}")

    def get_action(self, action_name):
        """
        Возвращает действие по его имени.
        :param action_name: Имя действия.
        :return: Функция действия или None, если действие не найдено.
        """
        return self.actions.get(action_name)
    
    async def capture_screen_action(self, params):
        try:
            logging.info("[CAPTURE_SCREEN_ACTION] Начало захвата экрана.")
            
            # Тест захвата скриншота без OpenCV
            screenshot = pyautogui.screenshot()
            logging.info("[CAPTURE_SCREEN_ACTION] PyAutoGUI скриншот успешно сделан.")

            # Сохраняем заглушку для OpenCV
            save_path = params.get("save_path", "/tmp/screenshot_test.png")
            np_screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
            cv2.imwrite(save_path, np_screen)
            logging.info(f"[CAPTURE_SCREEN_ACTION] Скриншот сохранён в {save_path}.")
        except Exception as e:
            logging.error(f"[CAPTURE_SCREEN_ACTION] Ошибка: {e}")

    async def find_template_action(self, params):
        """
        Проверяет, есть ли указанный шаблон на экране.
        :param params: Словарь параметров с ключами:
                    - "template" (имя шаблона/папки)
                    - "threshold" (порог совпадения, опционально)
        """
        try:
            template_name = params.get("template", "")
            threshold = params.get("threshold", 0.8)

            if not template_name:
                logging.error("[FIND_TEMPLATE_ACTION] Параметр 'template' не указан.")
                return

            screen_service = ScreenService()
            if screen_service.is_template_on_screen(template_name, threshold):
                logging.info(f"[FIND_TEMPLATE_ACTION] Шаблон '{template_name}' найден.")
            else:
                logging.info(f"[FIND_TEMPLATE_ACTION] Шаблон '{template_name}' не найден.")
        except Exception as e:
            logging.error(f"[FIND_TEMPLATE_ACTION] Ошибка: {e}")

    async def click_template_action(self, params):
        """
        Ищет шаблон на экране и нажимает на него.
        :param params: Словарь параметров с ключами:
                    - "template" (имя шаблона/папки)
                    - "threshold" (порог совпадения, опционально)
        """
        try:
            template_name = params.get("template", "")
            threshold = params.get("threshold", 0.8)

            if not template_name:
                logging.error("[CLICK_TEMPLATE_ACTION] Параметр 'template' не указан.")
                return

            screen_service = ScreenService()
            mouse_controller = MouseController(config_path="/app/config/movement_profile.json")
            if screen_service.interact_with_template(template_name, mouse_controller, threshold):
                logging.info(f"[CLICK_TEMPLATE_ACTION] Успешное взаимодействие с шаблоном '{template_name}'.")
            else:
                logging.info(f"[CLICK_TEMPLATE_ACTION] Шаблон '{template_name}' не найден.")
        except Exception as e:
            logging.error(f"[CLICK_TEMPLATE_ACTION] Ошибка: {e}")

    
# Настройка логирования
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")

