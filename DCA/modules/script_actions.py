import subprocess
import logging
import asyncio
import pyautogui
import json
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
            "do_nothing": self.do_nothing,
            "set_streaming_play": self.set_streaming_play_action,
            "random_play": self.random_play_action,
            "set_streaming_pause": self.set_streaming_pause_action,
            "set_streaming_unfold": self.set_streaming_unfold_action,
            "set_streaming_fold": self.set_streaming_fold_action,
            "set_streaming_forward": self.set_streaming_forward_action,
            "set_streaming_backward": self.set_streaming_backward_action,
            "scrolling": self.scrolling_action,
            "set_streaming_like": self.set_streaming_like_action,
            "skip_ad": self.skip_ad_action,
            "click_play_small": self.click_play_small_action,
            "set_shuffle_on": self.set_shuffle_on_action,
            "set_shuffle_off": self.set_shuffle_off_action,
            "set_cycle_one": self.set_cycle_one_action,
            "set_cycle_off": self.set_cycle_off_action,
            "set_cycle_oneclick": self.set_cycle_oneclick_action,
            "set_cycle_on": self.set_cycle_on_action,
            "random_action": self.random_action,
            "scroll_and_click": self.scroll_and_click_action,
            "fast_scroll_up_and_click": self.fast_scroll_up_and_click_action,
            ###################### Сбор Плейлистов ######################
            "check_first_launch": self.check_first_launch_action,
            "click_search": self.click_search_action,
            "select_artist": self.select_artist_action,
            "open_albums_tab": self.open_albums_tab_action,
            "select_random_album": self.select_random_album_action,
            "collect_playlist_tracks": self.collect_playlist_tracks_action,
            "return_to_liked_music": self.return_to_liked_music_action,

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
            random_offset = duration * 0.05  # 5% от длительности
            randomized_duration = duration + random.uniform(-random_offset, random_offset)

            logging.info(f"[WAIT_ACTION] Задержка {randomized_duration:.2f} секунд "
                        f"(исходная {duration} секунд, рандомизация ±5%).")
            await asyncio.sleep(randomized_duration)  # Убедитесь, что sleep выполняется в правильном цикле
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
    
    async def random_action(self, params):
        """
        Выполняет случайное действие на основе заданных вероятностей.
        :param params: Словарь с ключом "probabilities", указывающим на веса действий.
        """
        try:
            probabilities = params.get("probabilities", {})
            actions = list(probabilities.keys())
            weights = list(probabilities.values())

            # Выбираем случайное действие
            chosen_action = random.choices(actions, weights=weights, k=1)[0]

            logging.info(f"[RANDOM_ACTION] Выбрано действие: {chosen_action}")
            action = self.get_action(chosen_action)
            if action:
                await action({})
            else:
                logging.warning(f"[RANDOM_ACTION] Неизвестное действие: {chosen_action}")
        except Exception as e:
            logging.error(f"[RANDOM_ACTION] Ошибка: {e}")

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
    async def do_nothing(self, params):
        """Ничего не делает."""
        logging.info("[DO_NOTHING] Ничего не делаем. Отдыхаем!")
    
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

    async def random_play_action(self, params):
        """
        Выполняет один из случайных вариантов действия 'Play':
        - Масштабная прокрутка вверх + Play
        - Цикл + Play
        - Чистый Play
        """
        try:
            threshold = params.get("threshold", 0.9)

            # Проверяем наличие темплейта pause (музыка воспроизводится)
            logging.info("[SET_STREAMING_PLAY_ACTION] Проверяем, воспроизводится ли музыка.")
            screen_service = ScreenService()

            if screen_service.is_template_on_screen("pause", threshold):
                logging.info("[SET_STREAMING_PLAY_ACTION] Музыка уже воспроизводится. Действия не требуются.")
                return # Если воспроизводится, прерываем выполнение
            
            probabilities = {
                "scroll_up_play": 34,  # Масштабная прокрутка вверх + Play
                "cycle_play": 33,      # Цикл + Play
                "pure_play": 33        # Чистый Play
            }

            # Выбираем действие случайно
            chosen_action = random.choices(list(probabilities.keys()), weights=list(probabilities.values()), k=1)[0]
            logging.info(f"[RANDOM_PLAY_ACTION] Выбрано действие: {chosen_action}")

            # Вызов соответствующей функции
            if chosen_action == "scroll_up_play":
                await self.fast_scroll_up_and_click_action({})
                await self.set_streaming_play_action({})
            elif chosen_action == "cycle_play":
                await self.set_cycle_on_action({})
                await self.set_streaming_play_action({})
            elif chosen_action == "pure_play":
                await self.set_streaming_play_action({})
        except Exception as e:
            logging.error(f"[RANDOM_PLAY_ACTION] Ошибка: {e}")

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
                    random_y_offset = random.uniform(4 * template_height, 6 * template_height)
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

    async def set_shuffle_on_action(self, params):
        """
        Устанавливает режим shuffle в положение ON.
        Проверяет наличие темплейта "shuffle_off". Если он есть, нажимает на кнопку для активации shuffle.
        Если "shuffle_off" не найден, shuffle уже включен, действия не требуются.
        :param params: Параметры действия (например, "threshold").
        """
        try:
            threshold = params.get("threshold", 0.95)

            # Проверяем наличие темплейта shuffle_off (shuffle выключен)
            logging.info("[SET_SHUFFLE_ON_ACTION] Проверяем, включен ли shuffle.")
            screen_service = ScreenService()
            mouse_controller = MouseController(self.project_dir)

            if not screen_service.is_template_on_screen("shuffle_off", threshold):
                logging.info("[SET_SHUFFLE_ON_ACTION] Shuffle уже включен. Действия не требуются.")
                return

            # Если shuffle выключен, ищем и нажимаем кнопку shuffle_off
            logging.info("[SET_SHUFFLE_ON_ACTION] Shuffle выключен. Ищем кнопку 'shuffle_off'.")
            if screen_service.is_template_on_screen("shuffle_off", threshold):
                logging.info("[SET_SHUFFLE_ON_ACTION] Кнопка 'shuffle_off' найдена. Выполняем клик.")
                screen_service.interact_with_template("shuffle_off", mouse_controller, threshold)

                # Небольшая задержка после нажатия
                await asyncio.sleep(2)

                # Повторно проверяем наличие темплейта shuffle_on
                if screen_service.is_template_on_screen("shuffle_on", threshold):
                    logging.info("[SET_SHUFFLE_ON_ACTION] Shuffle успешно включен.")
                else:
                    logging.error("[SET_SHUFFLE_ON_ACTION] Не удалось включить shuffle. Проверьте шаблоны или приложение.")
            else:
                logging.error("[SET_SHUFFLE_ON_ACTION] Кнопка 'shuffle_off' не найдена. Проверьте шаблоны.")
        except Exception as e:
            logging.error(f"[SET_SHUFFLE_ON_ACTION] Ошибка: {e}")

    async def set_shuffle_off_action(self, params):
        """
        Устанавливает режим shuffle в положение OFF.
        Проверяет наличие темплейта "shuffle_on". Если он есть, нажимает на кнопку для отключения shuffle.
        Если "shuffle_on" не найден, shuffle уже выключен, действия не требуются.
        :param params: Параметры действия (например, "threshold").
        """
        try:
            threshold = params.get("threshold", 0.95)

            # Проверяем наличие темплейта shuffle_on (shuffle включен)
            logging.info("[SET_SHUFFLE_OFF_ACTION] Проверяем, выключен ли shuffle.")
            screen_service = ScreenService()
            mouse_controller = MouseController(self.project_dir)

            if not screen_service.is_template_on_screen("shuffle_on", threshold):
                logging.info("[SET_SHUFFLE_OFF_ACTION] Shuffle уже выключен. Действия не требуются.")
                return

            # Если shuffle включен, ищем и нажимаем кнопку shuffle_on
            logging.info("[SET_SHUFFLE_OFF_ACTION] Shuffle включен. Ищем кнопку 'shuffle_on'.")
            if screen_service.is_template_on_screen("shuffle_on", threshold):
                logging.info("[SET_SHUFFLE_OFF_ACTION] Кнопка 'shuffle_on' найдена. Выполняем клик.")
                screen_service.interact_with_template("shuffle_on", mouse_controller, threshold)

                # Небольшая задержка после нажатия
                await asyncio.sleep(2)

                # Повторно проверяем наличие темплейта shuffle_off
                if screen_service.is_template_on_screen("shuffle_off", threshold):
                    logging.info("[SET_SHUFFLE_OFF_ACTION] Shuffle успешно выключен.")
                else:
                    logging.error("[SET_SHUFFLE_OFF_ACTION] Не удалось выключить shuffle. Проверьте шаблоны или приложение.")
            else:
                logging.error("[SET_SHUFFLE_OFF_ACTION] Кнопка 'shuffle_on' не найдена. Проверьте шаблоны.")
        except Exception as e:
            logging.error(f"[SET_SHUFFLE_OFF_ACTION] Ошибка: {e}")

    async def set_cycle_one_action(self, params):
        """
        Устанавливает режим циклического воспроизведения в положение ONE (cycle_one).
        Если cycle_one не найден, ищет и переключает cycle_on или cycle_off до достижения состояния cycle_one.
        """
        try:
            threshold = params.get("threshold", 0.97)
            screen_service = ScreenService()
            mouse_controller = MouseController(self.project_dir)

            logging.info("[SET_CYCLE_ONE_ACTION] Устанавливаем cycle в положение ONE.")

            # Проверяем наличие темплейта cycle_one
            for attempt in range(5):  # Пытаемся максимум 5 раз
                if screen_service.is_template_on_screen("cycle_one", threshold):
                    logging.info("[SET_CYCLE_ONE_ACTION] Cycle установлен в положение ONE.")
                    return

                # Ищем и переключаем cycle_on
                if screen_service.is_template_on_screen("cycle_on", threshold):
                    logging.info("[SET_CYCLE_ONE_ACTION] Найден cycle_on. Выполняем клик.")
                    screen_service.interact_with_template("cycle_on", mouse_controller, threshold)
                    await self._move_mouse_away_randomly("cycle_on", mouse_controller)
                    await asyncio.sleep(1)
                    continue

                # Ищем и переключаем cycle_off
                if screen_service.is_template_on_screen("cycle_off", threshold):
                    logging.info("[SET_CYCLE_ONE_ACTION] Найден cycle_off. Выполняем клик.")
                    screen_service.interact_with_template("cycle_off", mouse_controller, threshold)
                    await self._move_mouse_away_randomly("cycle_off", mouse_controller)
                    await asyncio.sleep(1)
                    continue

            logging.error("[SET_CYCLE_ONE_ACTION] Не удалось установить положение ONE. Проверьте темплейты.")
        except Exception as e:
            logging.error(f"[SET_CYCLE_ONE_ACTION] Ошибка: {e}")

    async def _move_mouse_away_randomly(self, template_name, mouse_controller):
        """
        Отводит мышь на случайное расстояние после клика по темплейту.
        """
        try:
            screen_service = ScreenService()
            template_location = screen_service.get_template_location(template_name)

            if template_location:
                x, y, width, height = template_location

                # Рассчитываем смещение
                offset_x = random.randint(int(width * 0.05), int(width * 0.1))
                offset_y = random.randint(int(height * 1), int(height * 1.5))

                # Увеличиваем смещение для отведения мыши вниз
                target_x = x + width // 2 + offset_x
                target_y = y + height + offset_y

                mouse_controller.move_to(target_x, target_y)
                logging.info(f"[MOVE_MOUSE_AWAY] Мышь перемещена в точку: ({target_x}, {target_y}).")
        except Exception as e:
            logging.error(f"[MOVE_MOUSE_AWAY] Ошибка: {e}")

    async def set_cycle_off_action(self, params):
        """
        Устанавливает режим циклического воспроизведения в положение OFF.
        Один клик по cycle_one.
        """
        try:
            threshold = params.get("threshold", 0.9)

            # Устанавливаем cycle_one
            await self.set_cycle_one_action(params)

            # Выполняем один клик по cycle_one для перехода в OFF
            screen_service = ScreenService()
            mouse_controller = MouseController(self.project_dir)
            logging.info("[SET_CYCLE_OFF_ACTION] Устанавливаем cycle в положение OFF.")

            screen_service.interact_with_template("cycle_one", mouse_controller, threshold)
            await asyncio.sleep(0.5)  # Небольшая задержка после клика

            logging.info("[SET_CYCLE_OFF_ACTION] Завершено. Cycle установлен в положение OFF.")
        except Exception as e:
            logging.error(f"[SET_CYCLE_OFF_ACTION] Ошибка: {e}")

    async def set_cycle_on_action(self, params):
        """
        Устанавливает режим циклического воспроизведения в положение ON.
        Два клика по cycle_one.
        """
        try:
            threshold = params.get("threshold", 0.9)

            # Устанавливаем cycle_one
            await self.set_cycle_one_action(params)

            # Выполняем два клика по cycle_one для перехода в ON
            screen_service = ScreenService()
            mouse_controller = MouseController(self.project_dir)
            logging.info("[SET_CYCLE_ON_ACTION] Устанавливаем cycle в положение ON.")

            for _ in range(2):
                screen_service.interact_with_template("cycle_one", mouse_controller, threshold)
                await asyncio.sleep(0.5)  # Небольшая задержка между кликами

            logging.info("[SET_CYCLE_ON_ACTION] Завершено. Cycle установлен в положение ON.")
        except Exception as e:
            logging.error(f"[SET_CYCLE_ON_ACTION] Ошибка: {e}")
    
    async def set_cycle_oneclick_action(self, params):
        """
        Один клик по темплейту cycle.
        """
        try:
            threshold = params.get("threshold", 0.9)

            # Выполняем один клик по cycle
            screen_service = ScreenService()
            mouse_controller = MouseController(self.project_dir)
            logging.info("[SET_CYCLE_ONECLICK] Выполняем один клик по cycle.")

            screen_service.interact_with_template("cycle_off", mouse_controller, threshold)
            await asyncio.sleep(0.5)  # Небольшая задержка после клика

            logging.info("[SET_CYCLE_ONECLICK] Завершено. Cycle нажат.")
        except Exception as e:
            logging.error(f"[SET_CYCLE_ONECLICK] Ошибка: {e}")

    async def scroll_and_click_action(self, params):
        """
        Последовательно выполняет scrolling_action и click_play_small_action.
        """
        try:
            logging.info("[SCROLL_AND_CLICK_ACTION] Начало выполнения.")
            
            # Выполнение scrolling_action
            await self.scrolling_action({})
            logging.info("[SCROLL_AND_CLICK_ACTION] scrolling_action выполнено.")
            
            # Выполнение click_play_small_action
            await self.click_play_small_action({})
            logging.info("[SCROLL_AND_CLICK_ACTION] click_play_small_action выполнено.")
            
        except Exception as e:
            logging.error(f"[SCROLL_AND_CLICK_ACTION] Ошибка: {e}")

    async def fast_scroll_up_and_click_action(self, params):
        """
        Быстро пролистывает плейлист вверх с использованием scrolling_action и выполняет click_play_small_action.
        """
        try:
            logging.info("[FAST_SCROLL_UP_AND_CLICK_ACTION] Начало выполнения.")

            # Рандомизация параметров прокрутки
            scroll_steps = random.randint(1, 3)  # Количество прокруток (3-7 раз)
            logging.info(f"[FAST_SCROLL_UP_AND_CLICK_ACTION] Выполняется {scroll_steps} прокруток вверх.")
            
            # Выполнение scrolling_action с параметрами
            for _ in range(scroll_steps):
                await self.scrolling_action({
                    "direction": "up",  # Направление прокрутки - вверх
                    "steps": random.randint(5, 10)  # Количество шагов в одном прокручивании
                })
                delay = random.uniform(0.01, 0.03)  # Рандомная задержка между прокрутками
                await asyncio.sleep(delay)
                logging.info(f"[FAST_SCROLL_UP_AND_CLICK_ACTION] Прокрутка вверх выполнена с задержкой {delay:.2f} сек.")

            logging.info("[FAST_SCROLL_UP_AND_CLICK_ACTION] Быстрая прокрутка вверх завершена.")

            # Выполнение click_play_small_action
            await self.click_play_small_action({})
            logging.info("[FAST_SCROLL_UP_AND_CLICK_ACTION] click_play_small_action выполнено.")
            
        except Exception as e:
            logging.error(f"[FAST_SCROLL_UP_AND_CLICK_ACTION] Ошибка: {e}")

############################ [END] Управление стримингами ############################

############################ [START] Сбор Плейлистов ############################
    async def check_first_launch_action(self, params):
        """
        Проверяет, является ли текущий запуск первым за день.
        Сохраняет дату последнего запуска в конфигурационном файле.
        """
        try:
            # Определяем каталог для хранения конфигов
            configs_dir = os.path.join(self.project_dir, "configs")
            os.makedirs(configs_dir, exist_ok=True)  # Создаём каталог, если его нет
            config_file = os.path.join(configs_dir, "launch_config.json")

            # Загружаем конфигурацию, если файл существует
            if os.path.exists(config_file):
                with open(config_file, "r", encoding="utf-8") as file:
                    config = json.load(file)
            else:
                config = {}

            today = time.strftime("%Y-%m-%d")  # Текущая дата в формате YYYY-MM-DD

            if config.get("last_launch") == today:
                logging.info("[CHECK_FIRST_LAUNCH] Сегодня запуск уже был.")
                return False

            # Обновляем дату последнего запуска
            config["last_launch"] = today
            with open(config_file, "w", encoding="utf-8") as file:
                json.dump(config, file, ensure_ascii=False, indent=4)

            logging.info("[CHECK_FIRST_LAUNCH] Это первый запуск за сегодня.")
            return True
        except Exception as e:
            logging.error(f"[CHECK_FIRST_LAUNCH] Ошибка: {e}")
            return False
    
    async def click_search_action(self, params):
        """
        Нажимает кнопку "search".
        Проверяет наличие темплейта "search" и кликает по нему, если найден.
        :param params: Параметры действия (например, "threshold").
        """
        try:
            threshold = params.get("threshold", 0.9)

            logging.info("[CLICK_SEARCH_ACTION] Ищем кнопку 'search'.")
            screen_service = ScreenService()
            mouse_controller = MouseController(self.project_dir)

            if screen_service.is_template_on_screen("search", threshold):
                logging.info("[CLICK_SEARCH_ACTION] Кнопка 'search' найдена. Выполняем клик.")
                screen_service.interact_with_template("search", mouse_controller, threshold)
            else:
                logging.error("[CLICK_SEARCH_ACTION] Кнопка 'search' не найдена. Проверьте шаблоны.")
        except Exception as e:
            logging.error(f"[CLICK_SEARCH_ACTION] Ошибка: {e}")

    async def select_artist_action(self, params):
        """
        Выбирает жанр из конфига (или создаёт новый), определяет случайного артиста 
        из белого списка и вводит его имя в строку поиска.
        :param params: Параметры действия.
        """
        try:
            # Определяем каталог для хранения конфигов и белых списков
            configs_dir = os.path.join(self.project_dir, "configs")
            white_list_file = os.path.join(configs_dir, "white_list.json")
            config_file = os.path.join(configs_dir, "playlist_config.json")

            os.makedirs(configs_dir, exist_ok=True)  # Создаём каталог, если его нет

            # Проверяем наличие white_list.json
            if not os.path.exists(white_list_file):
                logging.error("[SELECT_ARTIST_ACTION] Файл white_list.json не найден.")
                return

            # Загружаем white_list.json
            with open(white_list_file, "r", encoding="utf-8") as file:
                white_list = json.load(file)

            # Проверяем или создаём конфиг
            if os.path.exists(config_file):
                with open(config_file, "r", encoding="utf-8") as file:
                    config = json.load(file)
            else:
                # Если конфига нет, создаём его с случайным жанром из доступных
                available_genres = list(white_list.keys())
                selected_genre = random.choice(available_genres)
                config = {"genre": selected_genre}
                with open(config_file, "w", encoding="utf-8") as file:
                    json.dump(config, file, ensure_ascii=False, indent=4)
                logging.info(f"[SELECT_ARTIST_ACTION] Новый конфиг создан с жанром: {selected_genre}")

            # Получаем жанр из конфига
            selected_genre = config.get("genre")
            logging.info(f"[SELECT_ARTIST_ACTION] Выбран жанр: {selected_genre}")

            if selected_genre not in white_list:
                logging.error(f"[SELECT_ARTIST_ACTION] Жанр {selected_genre} отсутствует в white_list.json.")
                return

            # Определяем артиста с заданными вероятностями
            artist_source = random.choices(
                ["our_artists", "external_artists"],
                weights=[34, 66],
                k=1
            )[0]

            if artist_source in white_list[selected_genre]:
                artist_list = white_list[selected_genre][artist_source]
                if not artist_list:
                    logging.error(f"[SELECT_ARTIST_ACTION] Список {artist_source} для жанра {selected_genre} пуст.")
                    return
                artist = random.choice(artist_list)
                logging.info(f"[SELECT_ARTIST_ACTION] Выбран артист: {artist} ({artist_source})")
            else:
                logging.error(f"[SELECT_ARTIST_ACTION] Источник {artist_source} отсутствует в жанре {selected_genre}.")
                return
            
            await asyncio.sleep(random.uniform(0.7, 2.0))  # Эмуляция естественной задержки

            # Вводим имя артиста в строку поиска
            logging.info(f"[SELECT_ARTIST_ACTION] Ввод имени артиста в строку поиска: {artist}")
            for char in artist:
                pyautogui.typewrite(char)
                await asyncio.sleep(random.uniform(0.05, 0.1))  # Эмуляция естественной задержки

            await asyncio.sleep(random.uniform(1.0, 2.1))  # Эмуляция естественной задержки

            # Выполняем поиск (Enter)
            pyautogui.press("enter")
            logging.info("[SELECT_ARTIST_ACTION] Поиск выполнен.")

        except Exception as e:
            logging.error(f"[SELECT_ARTIST_ACTION] Ошибка: {e}")

    async def open_albums_tab_action(self, params):
        """
        Ищет темплейт album на экране и кликает по нему.
        :param params: Параметры действия, такие как "threshold" для порога совпадения.
        """
        try:
            threshold = params.get("threshold", 0.8)  # Порог совпадения по умолчанию
            logging.info("[OPEN_ALBUMS_TAB_ACTION] Начинаем поиск темплейта album.")

            # Инициализация ScreenService и MouseController
            screen_service = ScreenService()
            mouse_controller = MouseController(self.project_dir)

            # Проверяем наличие темплейта "album"
            if screen_service.is_template_on_screen("albums", threshold):
                logging.info("[OPEN_ALBUMS_TAB_ACTION] Темплейт album найден. Выполняем клик.")

                # Выполняем клик по найденному темплейту
                if screen_service.interact_with_template("albums", mouse_controller, threshold):
                    logging.info("[OPEN_ALBUMS_TAB_ACTION] Клик по темплейту album выполнен успешно.")
                else:
                    logging.error("[OPEN_ALBUMS_TAB_ACTION] Не удалось взаимодействовать с темплейтом album.")
            else:
                logging.error("[OPEN_ALBUMS_TAB_ACTION] Темплейт album не найден. Проверьте наличие шаблона.")

        except Exception as e:
            logging.error(f"[OPEN_ALBUMS_TAB_ACTION] Ошибка: {e}")    
    

    async def select_random_album_action(self, params):
        """
        Выбирает случайный альбом на экране из доступных темплейтов и запускает его воспроизведение.
        :param params: Параметры действия (например, "threshold").
        """
        try:
            threshold = params.get("threshold", 0.9)

            logging.info("[SELECT_RANDOM_ALBUM_ACTION] Поиск темплейта albums для позиционирования.")
            screen_service = ScreenService()
            mouse_controller = MouseController(self.project_dir)

            # Определяем координаты якорного темплейта "albums"
            if screen_service.is_template_on_screen("albums", threshold):
                logging.info("[SELECT_RANDOM_ALBUM_ACTION] Темплейт 'albums' найден.")
                template_location = screen_service.get_template_location("albums", threshold)

                if template_location:
                    template_x, template_y, template_width, template_height = template_location

                    # Сдвигаем мышь вниз относительно высоты темплейта "albums"
                    random_y_offset = random.uniform(4 * template_height, 6 * template_height)
                    target_x = template_x + template_width // 2
                    target_y = template_y + random_y_offset

                    mouse_controller.move_to(int(target_x), int(target_y))
                    logging.info(f"[SELECT_RANDOM_ALBUM_ACTION] Мышь позиционирована в точку ({target_x}, {target_y}).")

                    # Выполняем случайный скроллинг или пропускаем его
                    if random.choice([True, False]):
                        await asyncio.sleep(0.5)
                        direction = random.choice(["up", "down"])
                        steps = random.randint(1, 3)
                        for _ in range(steps):
                            pyautogui.scroll(-1 if direction == "down" else 1)
                            await asyncio.sleep(random.uniform(0.2, 0.5))
                        logging.info("[SELECT_RANDOM_ALBUM_ACTION] Случайный скроллинг выполнен.")
                    else:
                        logging.info("[SELECT_RANDOM_ALBUM_ACTION] Случайный скроллинг пропущен.")

                    # Используем target_template для наведения на случайный альбом
                    logging.info("[SELECT_RANDOM_ALBUM_ACTION] Поиск и наведение на случайный альбом.")
                    if screen_service.target_template("choose_album", mouse_controller, threshold):
                        logging.info("[SELECT_RANDOM_ALBUM_ACTION] Наведение на случайный альбом выполнено успешно.")

                        # Выполняем click_play_small_action для запуска воспроизведения
                        await self.click_play_small_action({})
                        logging.info("[SELECT_RANDOM_ALBUM_ACTION] Воспроизведение альбома запущено.")
                    else:
                        logging.error("[SELECT_RANDOM_ALBUM_ACTION] Темплейты 'choose_album' не найдены.")
                        return
                else:
                    logging.error("[SELECT_RANDOM_ALBUM_ACTION] Не удалось определить координаты темплейта 'albums'.")
                    return
            else:
                logging.error("[SELECT_RANDOM_ALBUM_ACTION] Темплейт 'albums' не найден. Проверьте шаблоны.")
                return

        except Exception as e:
            logging.error(f"[SELECT_RANDOM_ALBUM_ACTION] Ошибка: {e}")

    async def collect_playlist_tracks_action(self, params):
        """
        Сбор треков с периодической проверкой и проставлением лайков.
        :param params: Параметры действия, такие как "like_probability" (вероятность вызова set_streaming_like).
        """
        try:
            # Устанавливаем временные рамки для сбора
            collection_duration = random.randint(300, 1800)  # (300, 1800) - 5–30 минут в секундах
            start_time = time.time()
            end_time = start_time + collection_duration
            logging.info(f"[COLLECT_PLAYLIST_TRACKS_ACTION] Сбор треков начат. Длительность: {collection_duration // 60} минут.")

            # Вероятность вызова set_streaming_like
            like_probability = params.get("like_probability", 15)  # По умолчанию 15%

            while time.time() < end_time:
                # Случайный интервал между итерациями (30–60 секунд)
                wait_time = random.randint(30, 60)
                await asyncio.sleep(wait_time)
                logging.info(f"[COLLECT_PLAYLIST_TRACKS_ACTION] Пауза завершена. Интервал: {wait_time} секунд.")

                # Вероятностный вызов set_streaming_like
                if random.randint(1, 100) <= like_probability:
                    logging.info("[COLLECT_PLAYLIST_TRACKS_ACTION] Пытаемся поставить лайк текущему треку.")
                    await self.set_streaming_like_action({})

            logging.info("[COLLECT_PLAYLIST_TRACKS_ACTION] Сбор треков завершён.")
        except Exception as e:
            logging.error(f"[COLLECT_PLAYLIST_TRACKS_ACTION] Ошибка: {e}")


    async def return_to_liked_music_action(self, params):
        """
        Возвращает проигрывание на плейлист 'Liked Music'.
        Наводится или нажимает на темплейт 'liked_music' с вероятностью 50%,
        затем нажимает на 'liked_music_action'.
        """
        try:
            threshold = params.get("threshold", 0.9)  # Порог совпадения по умолчанию
            logging.info("[RETURN_TO_LIKED_MUSIC_ACTION] Начало выполнения.")

            screen_service = ScreenService()
            mouse_controller = MouseController(self.project_dir)

            # Проверяем наличие темплейта liked_music
            if screen_service.is_template_on_screen("liked_music", threshold):
                logging.info("[RETURN_TO_LIKED_MUSIC_ACTION] Темплейт 'liked_music' найден.")
                template_location = screen_service.get_template_location("liked_music", threshold)

                if template_location:
                    x, y, width, height = template_location
                    target_x = x + width // 2
                    target_y = y + height // 2

                    # Наведение или нажатие на темплейт 'liked_music' с вероятностью 50%
                    if random.choice([True, False]):
                        mouse_controller.move_to(target_x, target_y)
                        logging.info("[RETURN_TO_LIKED_MUSIC_ACTION] Наведение на темплейт 'liked_music'.")
                    else:
                        mouse_controller.move_to(target_x, target_y)
                        mouse_controller.click()
                        logging.info("[RETURN_TO_LIKED_MUSIC_ACTION] Нажатие на темплейт 'liked_music'.")
                else:
                    logging.error("[RETURN_TO_LIKED_MUSIC_ACTION] Не удалось определить координаты темплейта 'liked_music'.")
                    return
            else:
                logging.error("[RETURN_TO_LIKED_MUSIC_ACTION] Темплейт 'liked_music' не найден.")
                return

            # Нажатие на темплейт 'liked_music_action'
            logging.info("[RETURN_TO_LIKED_MUSIC_ACTION] Ищем темплейт 'liked_music_action'.")
            if screen_service.is_template_on_screen("liked_music_action", threshold):
                logging.info("[RETURN_TO_LIKED_MUSIC_ACTION] Темплейт 'liked_music_action' найден. Выполняем нажатие.")
                if screen_service.interact_with_template("liked_music_action", mouse_controller, threshold):
                    logging.info("[RETURN_TO_LIKED_MUSIC_ACTION] Нажатие на 'liked_music_action' выполнено успешно.")
                else:
                    logging.error("[RETURN_TO_LIKED_MUSIC_ACTION] Не удалось выполнить нажатие на 'liked_music_action'.")
            else:
                logging.error("[RETURN_TO_LIKED_MUSIC_ACTION] Темплейт 'liked_music_action' не найден. Проверьте шаблоны.")

        except Exception as e:
            logging.error(f"[RETURN_TO_LIKED_MUSIC_ACTION] Ошибка: {e}")

############################ [-END-] Сбор Плейлистов ############################