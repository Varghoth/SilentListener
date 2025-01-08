import subprocess
import logging
import asyncio
import pyautogui
import time
import cv2
import numpy as np
import threading
import os
import random
import pytesseract
from PIL import Image

from global_storage import get_full_path
from modules.screen_service import ScreenService
from modules.mouse_service import MouseController

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")

class ScriptActions:
    def __init__(self, loop):
        self.loop = loop
        self.project_dir = os.path.abspath("./")  # Абсолютный путь к проекту
        self.actions = {
            "log_message": self.log_message_action,
            "wait": self.wait_action,
            "capture_screen": self.capture_screen_action,
            "find_template": self.find_template_action,
            "click_template": self.click_template_action,
            "make_firefox_focus": self.make_firefox_focus_action,
            "select_youtube_tab": self.select_youtube_tab_action,
            ###################### Управление Стримингами ######################
            "set_streaming_play": self.set_streaming_play_action,
            "set_streaming_pause": self.set_streaming_pause_action,
            "set_streaming_unfold": self.set_streaming_unfold_action,
            "set_streaming_fold": self.set_streaming_fold_action,
            "set_streaming_forward": self.set_streaming_forward_action,
            "set_streaming_backward": self.set_streaming_backward_action,
            "scrolling": self.scrolling_action,
            "set_streaming_like": self.set_streaming_like_action,
            "skip_ad": self.skip_ad_action,
            "click_play_small": self.click_play_small_action,

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
        """
        try:
            template_name = params.get("template", "")
            threshold = params.get("threshold", 0.8)

            # Проверяем наличие папки config
            config_dir = os.path.join(self.project_dir, "./")
            os.makedirs(config_dir, exist_ok=True)

            # Передаем путь в MouseController
            mouse_controller = MouseController(config_dir)

            if not template_name:
                logging.error("[CLICK_TEMPLATE_ACTION] Параметр 'template' не указан.")
                return

            screen_service = ScreenService()
            if screen_service.interact_with_template(template_name, mouse_controller, threshold):
                logging.info(f"[CLICK_TEMPLATE_ACTION] Успешное взаимодействие с шаблоном '{template_name}'.")
            else:
                logging.info(f"[CLICK_TEMPLATE_ACTION] Шаблон '{template_name}' не найден.")
        except Exception as e:
            logging.error(f"[CLICK_TEMPLATE_ACTION] Ошибка: {e}")

    async def make_firefox_focus_action(self, params):
        """
        Проверяет, находится ли Firefox в фокусе, и при необходимости выполняет действия для его активации.
        :param params: Параметры действия (например, "threshold").
        """
        try:
            threshold = params.get("threshold", 0.9)

            # Шаг 1: Проверка, находится ли Firefox в фокусе
            logging.info("[MAKE_FIREFOX_FOCUS_ACTION] Проверяем, находится ли Firefox в фокусе.")
            screen_service = ScreenService()
            if screen_service.is_template_on_screen("firefox_focus", threshold):
                logging.info("[MAKE_FIREFOX_FOCUS_ACTION] Firefox уже в фокусе. Действия не требуются.")
                return

            # Шаг 2: Проверка, запущен ли Firefox
            logging.info("[MAKE_FIREFOX_FOCUS_ACTION] Проверяем, запущен ли Firefox.")
            if screen_service.is_template_on_screen("firefox", threshold):
                logging.info("[MAKE_FIREFOX_FOCUS_ACTION] Firefox запущен, но не в фокусе. Кликаем на него.")
                mouse_controller = MouseController(self.project_dir)
                screen_service.interact_with_template("firefox", mouse_controller, threshold)
                return

            # Шаг 3: Запуск браузера, если Firefox не найден
            logging.info("[MAKE_FIREFOX_FOCUS_ACTION] Firefox не запущен. Ищем и запускаем браузер.")
            if screen_service.is_template_on_screen("browser", threshold):
                mouse_controller = MouseController(self.project_dir)
                screen_service.interact_with_template("browser", mouse_controller, threshold)
                await asyncio.sleep(5)  # Ждем загрузки Firefox

                # Повторная проверка, запущен ли Firefox
                if screen_service.is_template_on_screen("firefox_focus", threshold):
                    logging.info("[MAKE_FIREFOX_FOCUS_ACTION] Firefox успешно запущен.")
                else:
                    logging.error("[MAKE_FIREFOX_FOCUS_ACTION] Firefox не запустился. Проверьте шаблоны.")
            else:
                logging.error("[MAKE_FIREFOX_FOCUS_ACTION] Браузер не найден. Проверьте шаблоны.")
        except Exception as e:
            logging.error(f"[MAKE_FIREFOX_FOCUS_ACTION] Ошибка: {e}")

    async def select_youtube_tab_action(self, params):
        """
        Проверяет наличие шаблона вкладки YouTube и нажимает на него, если он найден.
        :param params: Параметры действия (например, "threshold").
        """
        try:
            threshold = params.get("threshold", 0.9)

            # Проверяем наличие шаблона YouTube
            logging.info("[SELECT_YOUTUBE_TAB_ACTION] Проверяем наличие вкладки YouTube.")
            screen_service = ScreenService()
            mouse_controller = MouseController(self.project_dir)

            if screen_service.is_template_on_screen("youtube_music_tab", threshold):
                logging.info("[SELECT_YOUTUBE_TAB_ACTION] Вкладка YouTube найдена. Выполняем клик.")
                screen_service.interact_with_template("youtube_music_tab", mouse_controller, threshold)
            else:
                logging.error("[SELECT_YOUTUBE_TAB_ACTION] Вкладка YouTube не найдена. Проверьте шаблоны.")
        except Exception as e:
            logging.error(f"[SELECT_YOUTUBE_TAB_ACTION] Ошибка: {e}")

############################ [START] Управление стримингами ############################
    async def set_streaming_play_action(self, params):
        """
        Устанавливает режим воспроизведения музыки (Play).
        Проверяет наличие темплейта "pause". Если он есть, воспроизведение уже запущено.
        Если "pause" не найден, нажимает на кнопку "play" и проверяет ещё раз.
        :param params: Параметры действия (например, "threshold").
        """
        try:
            threshold = params.get("threshold", 0.9)

            # Проверяем наличие темплейта pause (музыка воспроизводится)
            logging.info("[SET_STREAMING_PLAY_ACTION] Проверяем, воспроизводится ли музыка.")
            screen_service = ScreenService()
            mouse_controller = MouseController(self.project_dir)

            if screen_service.is_template_on_screen("pause", threshold):
                logging.info("[SET_STREAMING_PLAY_ACTION] Музыка уже воспроизводится. Действия не требуются.")
                return

            # Если музыка не воспроизводится, ищем кнопку play
            logging.info("[SET_STREAMING_PLAY_ACTION] Музыка не воспроизводится. Ищем кнопку 'play'.")
            if screen_service.is_template_on_screen("play", threshold):
                logging.info("[SET_STREAMING_PLAY_ACTION] Кнопка 'play' найдена. Выполняем клик.")
                screen_service.interact_with_template("play", mouse_controller, threshold)

                # Небольшая задержка после нажатия play
                await asyncio.sleep(2)

                # Повторно проверяем наличие темплейта pause
                if screen_service.is_template_on_screen("pause", threshold):
                    logging.info("[SET_STREAMING_PLAY_ACTION] Музыка успешно запущена.")
                else:
                    logging.error("[SET_STREAMING_PLAY_ACTION] Музыка не запустилась. Проверьте шаблоны или приложение.")
            else:
                logging.error("[SET_STREAMING_PLAY_ACTION] Кнопка 'play' не найдена. Проверьте шаблоны.")
        except Exception as e:
            logging.error(f"[SET_STREAMING_PLAY_ACTION] Ошибка: {e}")

    async def set_streaming_pause_action(self, params):
        """
        Устанавливает режим паузы воспроизведения музыки.
        Проверяет наличие темплейта "play". Если он есть, музыка уже на паузе.
        Если "play" не найден, нажимает на кнопку "pause" и проверяет ещё раз.
        :param params: Параметры действия (например, "threshold").
        """
        try:
            threshold = params.get("threshold", 0.9)

            # Проверяем наличие темплейта play (музыка на паузе)
            logging.info("[SET_STREAMING_PAUSE_ACTION] Проверяем, воспроизводится ли музыка.")
            screen_service = ScreenService()
            mouse_controller = MouseController(self.project_dir)

            if screen_service.is_template_on_screen("play", threshold):
                logging.info("[SET_STREAMING_PAUSE_ACTION] Музыка уже на паузе. Действия не требуются.")
                return

            # Если музыка воспроизводится, ищем кнопку pause
            logging.info("[SET_STREAMING_PAUSE_ACTION] Музыка воспроизводится. Ищем кнопку 'pause'.")
            if screen_service.is_template_on_screen("pause", threshold):
                logging.info("[SET_STREAMING_PAUSE_ACTION] Кнопка 'pause' найдена. Выполняем клик.")
                screen_service.interact_with_template("pause", mouse_controller, threshold)

                # Небольшая задержка после нажатия pause
                await asyncio.sleep(2)

                # Повторно проверяем наличие темплейта play
                if screen_service.is_template_on_screen("play", threshold):
                    logging.info("[SET_STREAMING_PAUSE_ACTION] Музыка успешно поставлена на паузу.")
                else:
                    logging.error("[SET_STREAMING_PAUSE_ACTION] Музыка не остановилась. Проверьте шаблоны или приложение.")
            else:
                logging.error("[SET_STREAMING_PAUSE_ACTION] Кнопка 'pause' не найдена. Проверьте шаблоны.")
        except Exception as e:
            logging.error(f"[SET_STREAMING_PAUSE_ACTION] Ошибка: {e}")

    async def set_streaming_unfold_action(self, params):
        """
        Устанавливает стриминг в развернутый режим, в котором виден плейлист.
        Проверяет наличие темплейта "fold". Если он есть, плеер уже развернут.
        Если "fold" не найден, нажимает на кнопку "unfold" и проверяет ещё раз.
        :param params: Параметры действия (например, "threshold").
        """
        try:
            threshold = params.get("threshold", 0.9)

            # Проверяем наличие темплейта fold (плеер развернут)
            logging.info("[SET_STREAMING_UNFOLD_ACTION] Проверяем, развернут ли плеер.")
            screen_service = ScreenService()
            mouse_controller = MouseController(self.project_dir)

            if screen_service.is_template_on_screen("fold", threshold):
                logging.info("[SET_STREAMING_UNFOLD_ACTION] Плеер развернут. Действия не требуются.")
                return

            # Если плеер свернут, ищем кнопку unfold
            logging.info("[SET_STREAMING_UNFOLD_ACTION] Плеер свернут. Ищем кнопку 'unfold'.")
            if screen_service.is_template_on_screen("unfold", threshold):
                logging.info("[SET_STREAMING_UNFOLD_ACTION] Кнопка 'unfold' найдена. Выполняем клик.")
                screen_service.interact_with_template("unfold", mouse_controller, threshold)

                # Небольшая задержка после нажатия unfold
                await asyncio.sleep(2)

                # Повторно проверяем наличие темплейта play
                if screen_service.is_template_on_screen("fold", threshold):
                    logging.info("[SET_STREAMING_UNFOLD_ACTION] Плеер развернут.")
                else:
                    logging.error("[SET_STREAMING_UNFOLD_ACTION] Плеер не развернулся. Проверьте шаблоны или приложение.")
            else:
                logging.error("[SET_STREAMING_UNFOLD_ACTION] Кнопка 'fold' не найдена. Проверьте шаблоны.")
        except Exception as e:
            logging.error(f"[SET_STREAMING_UNFOLD_ACTION] Ошибка: {e}")

    async def set_streaming_fold_action(self, params):
        """
        Устанавливает стриминг в свернутый режим.
        Проверяет наличие темплейта "unfold". Если он есть, плеер уже свернут.
        Если "unfold" не найден, нажимает на кнопку "fold" и проверяет ещё раз.
        :param params: Параметры действия (например, "threshold").
        """
        try:
            threshold = params.get("threshold", 0.9)

            # Проверяем наличие темплейта unfold (плеер свернут)
            logging.info("[SET_STREAMING_FOLD_ACTION] Проверяем, свернут ли плеер.")
            screen_service = ScreenService()
            mouse_controller = MouseController(self.project_dir)

            if screen_service.is_template_on_screen("unfold", threshold):
                logging.info("[SET_STREAMING_FOLD_ACTION] Плеер уже свернут. Действия не требуются.")
                return

            # Если плеер развернут, ищем кнопку fold
            logging.info("[SET_STREAMING_FOLD_ACTION] Плеер развернут. Ищем кнопку 'fold'.")
            if screen_service.is_template_on_screen("fold", threshold):
                logging.info("[SET_STREAMING_FOLD_ACTION] Кнопка 'fold' найдена. Выполняем клик.")
                screen_service.interact_with_template("fold", mouse_controller, threshold)

                # Небольшая задержка после нажатия fold
                await asyncio.sleep(2)

                # Повторно проверяем наличие темплейта unfold
                if screen_service.is_template_on_screen("unfold", threshold):
                    logging.info("[SET_STREAMING_FOLD_ACTION] Плеер успешно свернут.")
                else:
                    logging.error("[SET_STREAMING_FOLD_ACTION] Плеер не свернулся. Проверьте шаблоны или приложение.")
            else:
                logging.error("[SET_STREAMING_FOLD_ACTION] Кнопка 'fold' не найдена. Проверьте шаблоны.")
        except Exception as e:
            logging.error(f"[SET_STREAMING_FOLD_ACTION] Ошибка: {e}")

    async def set_streaming_forward_action(self, params):
        """
        Нажимает кнопку "forward" (следующий трек).
        Проверяет наличие темплейта "forward" и кликает по нему, если найден.
        :param params: Параметры действия (например, "threshold").
        """
        try:
            threshold = params.get("threshold", 0.9)

            logging.info("[SET_STREAMING_FORWARD_ACTION] Ищем кнопку 'forward'.")
            screen_service = ScreenService()
            mouse_controller = MouseController(self.project_dir)

            if screen_service.is_template_on_screen("forward", threshold):
                logging.info("[SET_STREAMING_FORWARD_ACTION] Кнопка 'forward' найдена. Выполняем клик.")
                screen_service.interact_with_template("forward", mouse_controller, threshold)
            else:
                logging.error("[SET_STREAMING_FORWARD_ACTION] Кнопка 'forward' не найдена. Проверьте шаблоны.")
        except Exception as e:
            logging.error(f"[SET_STREAMING_FORWARD_ACTION] Ошибка: {e}")

    async def set_streaming_backward_action(self, params):
        """
        Нажимает кнопку "backward" (предыдущий трек).
        Проверяет наличие темплейта "backward" и кликает по нему, если найден.
        :param params: Параметры действия (например, "threshold").
        """
        try:
            threshold = params.get("threshold", 0.9)

            logging.info("[SET_STREAMING_BACKWARD_ACTION] Ищем кнопку 'backward'.")
            screen_service = ScreenService()
            mouse_controller = MouseController(self.project_dir)

            if screen_service.is_template_on_screen("backward", threshold):
                logging.info("[SET_STREAMING_BACKWARD_ACTION] Кнопка 'backward' найдена. Выполняем клик.")
                screen_service.interact_with_template("backward", mouse_controller, threshold)
            else:
                logging.error("[SET_STREAMING_BACKWARD_ACTION] Кнопка 'backward' не найдена. Проверьте шаблоны.")
        except Exception as e:
            logging.error(f"[SET_STREAMING_BACKWARD_ACTION] Ошибка: {e}")

    async def scrolling_action(self, params):
        """
        Позиционирует мышь перед скроллингом и выполняет скроллинг в заданном или случайном направлении.
        :param params: Параметры действия (например, "direction" и "steps").
                        direction: "up" или "down" (опционально).
                        steps: Количество шагов скроллинга (опционально).
        """
        try:
            threshold = params.get("threshold", 0.9)
            direction = params.get("direction", random.choice(["up", "down"]))
            steps = params.get("steps", random.randint(3, 10))

            # Проверяем наличие анкорного темплейта
            logging.info("[SCROLLING_ACTION] Проверяем анкорные темплейты для позиционирования.")
            screen_service = ScreenService()
            mouse_controller = MouseController(self.project_dir)

            if screen_service.is_template_on_screen("ancor_scrolling", threshold):
                logging.info("[SCROLLING_ACTION] Анкор 'SCROLLING' найден. Выполняем позиционирование.")
                template_location = screen_service.get_template_location("ancor_scrolling", threshold)

                if template_location:
                    template_x, template_y, template_width, template_height = template_location

                    # Сдвигаем мышь вниз относительно высоты темплейта
                    random_y_offset = random.uniform(2 * template_height, 6 * template_height)
                    target_x = template_x + template_width // 2
                    target_y = template_y + random_y_offset

                    mouse_controller.move_to(int(target_x), int(target_y))
                    logging.info(f"[SCROLLING_ACTION] Мышь позиционирована в точку ({target_x}, {target_y}).")
                else:
                    logging.error("[SCROLLING_ACTION] Не удалось определить координаты анкора.")
                    return
            else:
                logging.error("[SCROLLING_ACTION] Анкор 'SCROLLING' не найден. Проверьте шаблоны.")
                return

            # Выполняем скроллинг
            logging.info(f"[SCROLLING_ACTION] Выполняем скроллинг: направление '{direction}', шаги {steps}.")
            for _ in range(steps):
                if direction == "up":
                    pyautogui.scroll(1)
                elif direction == "down":
                    pyautogui.scroll(-1)
                await asyncio.sleep(random.uniform(0.2, 0.5))  # Рандомная задержка между шагами
            logging.info("[SCROLLING_ACTION] Скроллинг завершен.")
        except Exception as e:
            logging.error(f"[SCROLLING_ACTION] Ошибка: {e}")

    async def set_streaming_like_action(self, params):
        """
        Ставит лайк текущему треку.
        Проверяет наличие темплейта "like_off". Если он есть, нажимает на кнопку для постановки лайка.
        Если "like_off" не найден, лайк уже проставлен, действия не требуются.
        :param params: Параметры действия (например, "threshold").
        """
        try:
            threshold = params.get("threshold", 0.9)

            # Проверяем наличие темплейта like_off (лайк не поставлен)
            logging.info("[SET_STREAMING_LIKE_ACTION] Проверяем, установлен ли лайк.")
            screen_service = ScreenService()
            mouse_controller = MouseController(self.project_dir)

            if not screen_service.is_template_on_screen("like_off", threshold):
                logging.info("[SET_STREAMING_LIKE_ACTION] Лайк уже установлен. Действия не требуются.")
                return

            # Если лайк не установлен, ищем и нажимаем кнопку like_off
            logging.info("[SET_STREAMING_LIKE_ACTION] Лайк не установлен. Ищем кнопку 'like_off'.")
            if screen_service.is_template_on_screen("like_off", threshold):
                logging.info("[SET_STREAMING_LIKE_ACTION] Кнопка 'like_off' найдена. Выполняем клик.")
                screen_service.interact_with_template("like_off", mouse_controller, threshold)

                # Небольшая задержка после нажатия like
                await asyncio.sleep(2)

                # Повторно проверяем наличие темплейта like_on
                if screen_service.is_template_on_screen("like_on", threshold):
                    logging.info("[SET_STREAMING_LIKE_ACTION] Лайк успешно установлен.")
                else:
                    logging.error("[SET_STREAMING_LIKE_ACTION] Лайк не установился. Проверьте шаблоны или приложение.")
            else:
                logging.error("[SET_STREAMING_LIKE_ACTION] Кнопка 'like_off' не найдена. Проверьте шаблоны.")
        except Exception as e:
            logging.error(f"[SET_STREAMING_LIKE_ACTION] Ошибка: {e}")

    async def skip_ad_action(self, params):
        """
        Выполняет действия для исправления ошибок (например, пропуска рекламы).
        Проверяет наличие кнопки "Skip" на экране, используя как градации серого, так и высококонтрастные изображения.
        Если найдена, нажимает на нее.
        :param params: Параметры действия (например, "threshold").
        """
        try:
            threshold = params.get("threshold", 0.75)  # Порог совпадения
            logging.info("[ERROR_CORRECTION_ACTION] Проверяем наличие кнопки 'Skip'.")

            screen_service = ScreenService()
            mouse_controller = MouseController(self.project_dir)

            # Загружаем шаблон 'Skip' в высококонтрастном режиме
            skip_template_name = "skip_ad"
            skip_templates = screen_service.load_templates(skip_template_name)  # Цветные шаблоны
            skip_templates_gray = screen_service.load_templates_grayscale(skip_template_name)  # Шаблоны в градациях серого

            if not skip_templates and not skip_templates_gray:
                logging.error(f"[ERROR_CORRECTION_ACTION] Шаблоны 'Skip' не найдены в папке '{skip_template_name}'.")
                return

            # Делаем скриншот экрана
            screen_color = screen_service.capture_screen()  # Цветной скриншот
            screen_gray = screen_service.capture_screen_grayscale()  # Градации серого

            if screen_color is None or screen_gray is None:
                logging.error("[ERROR_CORRECTION_ACTION] Не удалось захватить экран. Пропускаем действие.")
                return

            # Обработка цветных шаблонов
            for template in skip_templates:
                result = cv2.matchTemplate(screen_color, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)

                if max_val >= threshold:
                    center_x = max_loc[0] + template.shape[1] // 2
                    center_y = max_loc[1] + template.shape[0] // 2

                    logging.info(f"[ERROR_CORRECTION_ACTION] Цветной шаблон 'Skip' найден. Центр: ({center_x}, {center_y}).")
                    mouse_controller.move_to(center_x, center_y)
                    mouse_controller.click()
                    await asyncio.sleep(2)  # Небольшая задержка после клика
                    return

            # Обработка шаблонов в градациях серого
            for template in skip_templates_gray:
                result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)

                if max_val >= threshold:
                    center_x = max_loc[0] + template.shape[1] // 2
                    center_y = max_loc[1] + template.shape[0] // 2

                    logging.info(f"[ERROR_CORRECTION_ACTION] Шаблон в градациях серого 'Skip' найден. Центр: ({center_x}, {center_y}).")
                    mouse_controller.move_to(center_x, center_y)
                    mouse_controller.click()
                    await asyncio.sleep(2)  # Небольшая задержка после клика
                    return

            logging.info("[ERROR_CORRECTION_ACTION] Кнопка 'Skip' не найдена на экране.")
        except Exception as e:
            logging.error(f"[ERROR_CORRECTION_ACTION] Ошибка: {e}")

    async def click_play_small_action(self, params):
        """
        Ищет и нажимает на кнопку 'play_small', используя шаблоны в градациях серого и высококонтрастный метод.
        :param params: Параметры действия (например, "threshold").
        """
        try:
            threshold = params.get("threshold", 0.8)  # Порог совпадения
            logging.info("[CLICK_PLAY_SMALL_ACTION] Проверяем наличие кнопки 'play_small'.")

            screen_service = ScreenService()
            mouse_controller = MouseController(self.project_dir)

            # Загружаем шаблон 'play_small' в градациях серого
            play_small_template_name = "play_small"
            play_small_templates = screen_service.load_templates_grayscale(play_small_template_name)

            if not play_small_templates:
                logging.error(f"[CLICK_PLAY_SMALL_ACTION] Шаблон 'play_small' не найден в папке '{play_small_template_name}'.")
                return

            # Делаем скриншот экрана в градациях серого
            screen_gray = screen_service.capture_screen_grayscale()
            if screen_gray is None:
                logging.error("[CLICK_PLAY_SMALL_ACTION] Не удалось захватить экран. Пропускаем действие.")
                return

            # Ищем шаблон 'play_small' на экране
            for template in play_small_templates:
                # Применяем метод сравнения шаблонов
                result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)

                if max_val >= threshold:
                    # Если найдено совпадение, определяем координаты центра шаблона
                    center_x = max_loc[0] + template.shape[1] // 2
                    center_y = max_loc[1] + template.shape[0] // 2

                    logging.info(f"[CLICK_PLAY_SMALL_ACTION] Шаблон 'play_small' найден. Центр: ({center_x}, {center_y}).")
                    mouse_controller.move_to(center_x, center_y)
                    mouse_controller.click()
                    await asyncio.sleep(2)  # Небольшая задержка после клика
                    return

            logging.info("[CLICK_PLAY_SMALL_ACTION] Кнопка 'play_small' не найдена на экране.")
        except Exception as e:
            logging.error(f"[CLICK_PLAY_SMALL_ACTION] Ошибка: {e}")
