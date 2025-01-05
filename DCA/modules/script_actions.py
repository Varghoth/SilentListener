import subprocess
import logging
import asyncio
import pyautogui
import time
import cv2
import numpy as np
import pyautogui
import threading
cv2.setNumThreads(1)

from global_storage import get_full_path
from modules.screen_service import ScreenService

class ScriptActions:
    def __init__(self, loop):
        self.loop = loop
        self.actions = {
            "log_message": self.log_message_action,
            "wait": self.wait_action,
            "is_firefox_running": self.is_firefox_running,
            "capture_screen": self.capture_screen_action,
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
    
    def run_in_thread(target, *args, **kwargs):
        """
        Запускает функцию в отдельном потоке.
        """
        thread = threading.Thread(target=target, args=args, kwargs=kwargs, daemon=True)
        thread.start()
        return thread
    
    def is_firefox_running_in_thread():
        firefox_templates_path = get_full_path("templates/firefox")
        templates = ScreenService.load_templates(firefox_templates_path)

        if not templates:
            logging.error("Шаблоны для Firefox не найдены.")
            return False

        screen = ScreenService.capture_screen()
        if screen is None:
            logging.error("Ошибка захвата экрана. Проверка завершена.")
            return False

        is_running = ScreenService.match_templates_on_screen(screen, templates)
        return is_running


    async def is_firefox_running(self, params=None):
        """
        Проверяет, запущен ли Firefox.
        """
        try:
            thread = self.run_in_thread(self.is_firefox_running_in_thread)
            thread.join()  # Дождаться завершения потока
            logging.info("Проверка Firefox завершена.")
        except Exception as e:
            logging.error(f"Ошибка при проверке Firefox: {e}")

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

    
# Настройка логирования
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")

