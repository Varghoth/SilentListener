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
import re
import random
import shutil
import pytesseract
from PIL import Image
from datetime import datetime, timedelta

from global_storage import get_full_path
from modules.screen_service import ScreenService
from modules.mouse_service import MouseController

# Пути
EXTENSIONS_SRC_DIR = "/app/DCA/firefox_extensions"  # Каталог с сохранёнными расширениями
FIREFOX_EXTENSIONS_DIR = "/root/.mozilla/firefox/*.default-release/extensions"  # Каталог профиля Firefox

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")

class ScriptActions:
    def __init__(self, loop):
        self.loop = loop
        self.project_dir = os.path.abspath("./")  # Абсолютный путь к проекту
        self.actions = {
            "log_message": self.log_message_action,
            "wait": self.wait_action,
            "wait_interval": self.wait_interval_action,
            "capture_screen": self.capture_screen_action,
            "find_template": self.find_template_action,
            "click_template": self.click_template_action,
            "make_firefox_focus": self.make_firefox_focus_action,
            "select_youtube_tab": self.select_youtube_tab_action,
            "random_wait_and_shutdown": self.random_wait_and_shutdown_action,
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
            "no_interface_error": self.no_interface_error_action,
            ###################### Сбор Плейлистов ######################
            "check_first_launch": self.check_first_launch_action,
            "click_search": self.click_search_action,
            "select_artist": self.select_artist_action,
            "open_albums_tab": self.open_albums_tab_action,
            "select_random_album": self.select_random_album_action,
            "collect_playlist_tracks": self.collect_playlist_tracks_action,
            "return_to_liked_music": self.return_to_liked_music_action,
            "save_page": self.save_page_action,
            "parse_liked_tracks": self.parse_liked_tracks_action,
            "playlist_collection_workflow": self.playlist_collection_workflow,
            ###################### Fingerprint ######################
            "generate_user_profile": self.generate_user_profile_action,
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
    
    async def wait_interval_action(self, params):
        """
        Выполняет задержку с возможностью указания диапазона задержки в минутах.
        """
        try:
            min_minutes = params.get("min_minutes", 0)  # Минимальное значение в минутах
            max_minutes = params.get("max_minutes", min_minutes)  # Максимальное значение в минутах (по умолчанию равно min_minutes)
            randomization_percent = params.get("randomization_percent", 5)  # Процент рандомизации (по умолчанию ±5%)

            # Генерация случайной задержки в диапазоне
            base_duration = random.uniform(min_minutes, max_minutes) * 60  # Конвертируем минуты в секунды
            random_offset = base_duration * (randomization_percent / 100)  # Вычисляем рандомный оффсет
            randomized_duration = base_duration + random.uniform(-random_offset, random_offset)

            logging.info(f"[WAIT_ACTION] Задержка {randomized_duration:.2f} секунд "
                         f"(диапазон {min_minutes}-{max_minutes} минут, рандомизация ±{randomization_percent}%).")

            # Выполнение задержки
            await asyncio.sleep(randomized_duration)
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
        Проверяет, запущен ли Firefox, и запускает его в развернутом виде через командную строку, если необходимо.
        :param params: Параметры действия (например, "threshold").
        """
        try:
            threshold = params.get("threshold", 0.9)

            # Путь к Firefox и профилю
            firefox_dir = "/app/firefox"
            profile_dir = f"{firefox_dir}/profiles"

            # Убедимся, что каталог профилей существует
            os.makedirs(profile_dir, exist_ok=True)
            logging.info(f"[MAKE_FIREFOX_FOCUS_ACTION] Каталог профилей проверен: {profile_dir}")

            # Проверка: запущен ли Firefox
            logging.info("[MAKE_FIREFOX_FOCUS_ACTION] Проверяем, запущен ли Firefox.")
            result = subprocess.run(
                ["pgrep", "-f", f"{firefox_dir}/firefox"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            if result.returncode == 0:
                logging.info("[MAKE_FIREFOX_FOCUS_ACTION] Firefox уже запущен.")
            else:
                # Запуск Firefox с параметрами
                logging.info("[MAKE_FIREFOX_FOCUS_ACTION] Firefox не запущен. Запускаем браузер.")
                subprocess.Popen(
                    [
                        f"{firefox_dir}/firefox",
                        f"--profile",
                        f"{profile_dir}",
                        "--start-maximized"
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    env=os.environ.copy()
                )
                await asyncio.sleep(5)  # Ждем загрузки Firefox

            # Проверка: открыт ли Firefox в фокусе (если необходимо)
            logging.info("[MAKE_FIREFOX_FOCUS_ACTION] Проверяем, в фокусе ли Firefox.")
            screen_service = ScreenService()
            if not screen_service.is_template_on_screen("firefox_focus", threshold):
                logging.warning("[MAKE_FIREFOX_FOCUS_ACTION] Firefox запущен, но не в фокусе.")
                mouse_controller = MouseController(self.project_dir)
                screen_service.interact_with_template("firefox", mouse_controller, threshold)
            else:
                logging.info("[MAKE_FIREFOX_FOCUS_ACTION] Firefox в фокусе.")

        except Exception as e:
            logging.error(f"[MAKE_FIREFOX_FOCUS_ACTION] Ошибка: {e}")

    async def select_youtube_tab_action(self, params):
        """
        Проверяет наличие заголовка страницы YouTube и переключает вкладки, если он не найден.
        :param params: Параметры действия (например, "threshold").
        """
        try:
            threshold = params.get("threshold", 0.9)
            max_attempts = 12  # Максимальное количество попыток

            logging.info("[SELECT_YOUTUBE_TAB_ACTION] Проверяем наличие заголовка страницы YouTube.")
            screen_service = ScreenService()

            for attempt in range(max_attempts):
                logging.info(f"[SELECT_YOUTUBE_TAB_ACTION] Попытка {attempt + 1} из {max_attempts}.")

                # Проверяем наличие заголовка страницы YouTube
                if screen_service.is_template_on_screen("youtube_page_header", threshold):
                    logging.info("[SELECT_YOUTUBE_TAB_ACTION] Заголовок страницы YouTube найден. Продолжаем выполнение.")
                    return

                # Если заголовок не найден, переключаем вкладку
                logging.info("[SELECT_YOUTUBE_TAB_ACTION] Заголовок страницы YouTube не найден. Переключаем вкладку.")
                pyautogui.hotkey("ctrl", "tab")
                await asyncio.sleep(1)  # Небольшая задержка после переключения вкладки

            logging.error("[SELECT_YOUTUBE_TAB_ACTION] Не удалось найти заголовок страницы YouTube после максимального числа попыток.")

        except Exception as e:
            logging.error(f"[SELECT_YOUTUBE_TAB_ACTION] Ошибка: {e}")

    async def random_wait_and_shutdown_action(self, params):
        """
        Запускает асинхронный таймер, который выполняет действия по истечении времени.
        После выполнения таймер завершает ВСЁ.
        """
        async def run_timer():
            try:
                # Получаем параметры времени
                guaranteed_hours = params.get("guaranteed_hours", 0)
                guaranteed_minutes = params.get("guaranteed_minutes", 0)
                randomization_range = params.get("randomization_range_minutes", 0)
                actions = params.get("actions", [])

                # Переводим гарантированное время в секунды
                guaranteed_time = guaranteed_hours * 3600 + guaranteed_minutes * 60

                # Генерируем случайное время для рандомизации
                random_offset = random.randint(0, randomization_range * 60)

                # Итоговое время ожидания
                total_wait_time = guaranteed_time + random_offset
                logging.info(f"[RANDOM_WAIT_AND_SHUTDOWN_ACTION] Таймер запущен на {total_wait_time // 60} минут "
                            f"({guaranteed_hours} ч {guaranteed_minutes} мин + случайные {random_offset // 60} мин).")

                # Таймер
                await asyncio.sleep(total_wait_time)

                # Выполнение действий после ожидания
                if "shutdown_firefox" in actions:
                    logging.info("[RANDOM_WAIT_AND_SHUTDOWN_ACTION] Завершение процесса Firefox...")
                    try:
                        subprocess.run(["pkill", "-f", "firefox"], check=True)
                        logging.info("[RANDOM_WAIT_AND_SHUTDOWN_ACTION] Firefox успешно завершен.")
                    except subprocess.CalledProcessError as e:
                        logging.error(f"[RANDOM_WAIT_AND_SHUTDOWN_ACTION] Ошибка завершения Firefox: {e}")

                if "stop_dca" in actions:
                    logging.info("[RANDOM_WAIT_AND_SHUTDOWN_ACTION] Завершение процесса DCA...")
                    try:
                        subprocess.run(["pkill", "-f", "DCA"], check=True)
                        logging.info("[RANDOM_WAIT_AND_SHUTDOWN_ACTION] DCA успешно завершен.")
                    except subprocess.CalledProcessError as e:
                        logging.error(f"[RANDOM_WAIT_AND_SHUTDOWN_ACTION] Ошибка завершения DCA: {e}")

                # Завершение текущего скрипта
                logging.info("[RANDOM_WAIT_AND_SHUTDOWN_ACTION] Завершаем все процессы. Скрипт завершится через 5 секунд...")
                await asyncio.sleep(5)  # Небольшая задержка для логов
                os._exit(0)  # Полное завершение Python-процесса и всех связанных задач
            except Exception as e:
                logging.error(f"[RANDOM_WAIT_AND_SHUTDOWN_ACTION] Ошибка: {e}")
                os._exit(1)  # Завершение скрипта с ошибкой

        # Запуск таймера в фоне
        asyncio.create_task(run_timer())




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

                    # Проверяем и обновляем количество необходимых треков
                    analysis_results_path = "/app/DCA_configs/analysis_results.json"
                    if os.path.exists(analysis_results_path):
                        with open(analysis_results_path, "r+", encoding="utf-8") as file:
                            analysis_results = json.load(file)
                            tracks_to_add = analysis_results.get("tracks_to_add", {})
                            if tracks_to_add.get("count", 0) > 0:
                                tracks_to_add["count"] -= 1
                                logging.info(f"[SET_STREAMING_LIKE_ACTION] Уменьшено количество треков для добавления: {tracks_to_add['count']}")
                                file.seek(0)
                                json.dump(analysis_results, file, ensure_ascii=False, indent=4)
                                file.truncate()
                            else:
                                logging.info("[SET_STREAMING_LIKE_ACTION] Количество треков для добавления уже равно 0 или отсутствует.")
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

    async def no_interface_error_action(self, params):
        """
        Проверяет наличие темплейта 'no_interface_error' на экране.
        Если темплейт найден, выводит сообщение. Если не найден в течение трёх попыток,
        выполняет клавиатурную комбинацию ctrl+r для обновления страницы.
        :param params: Параметры действия (например, "threshold").
        """
        try:
            threshold = params.get("threshold", 0.75)  # Порог совпадения по умолчанию
            max_attempts = 3  # Максимальное количество попыток
            interval = 3  # Интервал между попытками в секундах

            logging.info("[NO_INTERFACE_ERROR_ACTION] Начало выполнения.")
            screen_service = ScreenService()

            for attempt in range(1, max_attempts + 1):
                logging.info(f"[NO_INTERFACE_ERROR_ACTION] Попытка {attempt} из {max_attempts}.")

                # Проверяем наличие темплейта 'no_interface_error'
                if screen_service.is_template_on_screen("no_interface_error", threshold):
                    logging.info("[NO_INTERFACE_ERROR_ACTION] Темплейт 'no_interface_error' найден.")
                    return  # Прерываем выполнение, если темплейт найден

                # Задержка перед следующей попыткой
                await asyncio.sleep(interval)

            # Если темплейт не найден после трёх попыток, выполняем ctrl+rs
            logging.info("[NO_INTERFACE_ERROR_ACTION] Темплейт 'no_interface_error' не найден. Обновляем страницу.")
            pyautogui.hotkey("ctrl", "r")
            logging.info("[NO_INTERFACE_ERROR_ACTION] Выполнена комбинация клавиш ctrl+r.")

            await asyncio.sleep(interval)
            await self.skip_ad_action(params)

            await asyncio.sleep(interval)
            await self.skip_ad_action(params)

        except Exception as e:
            logging.error(f"[NO_INTERFACE_ERROR_ACTION] Ошибка: {e}")

############################ [END] Управление стримингами ############################

############################ [START] Сбор Плейлистов ############################
    async def check_first_launch_action(self, params):
        """
        Проверяет, является ли текущий запуск первым за день.
        Сохраняет дату последнего запуска в конфигурационном файле.
        """
        try:
            # Определяем каталог для хранения конфигов
            configs_dir = "/app/DCA_configs"
            os.makedirs(configs_dir, exist_ok=True)  # Создаём каталог, если его нет
            config_file = os.path.join(configs_dir, "PlaylistCollect_first_launch.json")

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
        :param params: Параметры действия. Ожидаемые параметры:
            - "our_artist_weight" (вес для наших артистов)
            - "external_artist_weight" (вес для внешних артистов)
        """
        try:
            # Определяем каталог для хранения конфигов и белых списков
            configs_dir = os.path.join(self.project_dir, "configs")
            white_list_file = os.path.join(configs_dir, "white_list.json")
            ideal_balance_file = os.path.join(configs_dir, "ideal_balance.json")
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

            # Получаем вероятности из параметров, если они заданы
            our_artist_weight = params.get("our_artist_weight")
            external_artist_weight = params.get("external_artist_weight")

            # Если вероятности не переданы в параметрах, загружаем из ideal_balance.json
            if our_artist_weight is None or external_artist_weight is None:
                if not os.path.exists(ideal_balance_file):
                    logging.error("[SELECT_ARTIST_ACTION] Файл ideal_balance.json не найден.")
                    return

                with open(ideal_balance_file, "r", encoding="utf-8") as file:
                    ideal_balance = json.load(file).get("ideal_balance", {})

                our_artist_weight = ideal_balance.get("our_artists", 34)
                external_artist_weight = ideal_balance.get("external_artists", 66)

            logging.info(f"[SELECT_ARTIST_ACTION] Вероятности: our_artists={our_artist_weight}, external_artists={external_artist_weight}")

            # Определяем артиста с заданными вероятностями
            artist_source = random.choices(
                ["our_artists", "external_artists"],
                weights=[our_artist_weight, external_artist_weight],
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
            max_attempts = 3  # Максимальное количество попыток поиска темплейта

            logging.info("[SELECT_RANDOM_ALBUM_ACTION] Начало выполнения.")
            screen_service = ScreenService()
            mouse_controller = MouseController(self.project_dir)

            # Попытки найти темплейт 'albums'
            template_location = None
            for attempt in range(1, max_attempts + 1):
                logging.info(f"[SELECT_RANDOM_ALBUM_ACTION] Попытка {attempt} поиска темплейта 'albums'.")
                if screen_service.is_template_on_screen("albums", threshold):
                    template_location = screen_service.get_template_location("albums", threshold)
                    if template_location:
                        logging.info(f"[SELECT_RANDOM_ALBUM_ACTION] Темплейт 'albums' найден на попытке {attempt}.")
                        break
                await asyncio.sleep(0.5)  # Задержка перед следующей попыткой

            if not template_location:
                logging.error(f"[SELECT_RANDOM_ALBUM_ACTION] Темплейт 'albums' не найден после {max_attempts} попыток.")
                return

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

            await self.set_streaming_play_action({}) # На всякий случай запускаем воспроизведение (а то бывали случаи)

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

    async def run_def_collection_action(self, params):
        """
        Сервисная функция, осуществляющая сбор плейлистов по-умолчанию (вероятности из ideal_balance.json).
        Выполняет все действия последовательно, с возможностью добавления логики.
        """
        try:
            logging.info("[DEF_PLAYLIST_COLLECT] Начало ДЕФОЛТНОГО сбора плейлистов.")

            await asyncio.sleep(5)  # Задержка для загрузки

            # 1. Пропускаем рекламу (дважды, на случай задержки)
            await self.skip_ad_action(params)
            await self.skip_ad_action(params)

            # 2. Нажимаем на кнопку поиска
            await self.click_search_action(params)

            # 3. Выбираем случайного артиста и вводим его в строку поиска
            #await self.select_artist_action({})
            await self.select_artist_action({})

            # 4. Ждем загрузки результатов поиска
            await asyncio.sleep(params.get("wait_after_search", 4))

            # 5. Открываем вкладку альбомов
            await self.open_albums_tab_action(params)

            # 6. Ждем загрузки вкладки альбомов
            await asyncio.sleep(params.get("wait_after_albums", 2))

            # 7. Выбираем случайный альбом и запускаем его воспроизведение
            await self.select_random_album_action(params)

            # 8. Собираем треки из плейлиста
            await self.collect_playlist_tracks_action(params)

            logging.info("[DEF_PLAYLIST_COLLECT] Рабочий процесс сбора плейлистов завершен успешно.")

        except Exception as e:
            logging.error(f"[DEF_PLAYLIST_COLLECT] Ошибка выполнения рабочего процесса: {e}")

    async def run_our_artists_collection_action(self, params):
        """
        Сервисная функция, осуществляющая сбор плейлистов только из our_artists.
        Выполняет все действия последовательно, с возможностью добавления логики.
        """
        try:
            logging.info("[OUR_PLAYLIST_COLLECT] Начало OUR_ARTISTS сбора плейлистов.")

            await asyncio.sleep(5)  # Задержка для загрузки

            # 1. Пропускаем рекламу (дважды, на случай задержки)
            await self.skip_ad_action(params)
            await self.skip_ad_action(params)

            # 2. Нажимаем на кнопку поиска
            await self.click_search_action(params)

            # 3. Выбираем нашего артиста и вводим его в строку поиска
            await self.select_artist_action({
                "our_artist_weight": 100,
                "external_artist_weight": 0
            })

            # 4. Ждем загрузки результатов поиска
            await asyncio.sleep(params.get("wait_after_search", 4))

            # 5. Открываем вкладку альбомов
            await self.open_albums_tab_action(params)

            # 6. Ждем загрузки вкладки альбомов
            await asyncio.sleep(params.get("wait_after_albums", 2))

            # 7. Выбираем случайный альбом и запускаем его воспроизведение
            await self.select_random_album_action(params)

            # 8. Собираем треки из плейлиста
            await self.collect_playlist_tracks_action(params)

            logging.info("[OUR_PLAYLIST_COLLECT] Рабочий процесс сбора плейлистов завершен успешно.")

        except Exception as e:
            logging.error(f"[OUR_PLAYLIST_COLLECT] Ошибка выполнения рабочего процесса: {e}")

    async def run_external_artists_collection_action(self, params):
        """
        Сервисная функция, осуществляющая сбор плейлистов только из external_artists.
        Выполняет все действия последовательно, с возможностью добавления логики.
        """
        try:
            logging.info("[EXTERNAL_PLAYLIST_COLLECT] Начало EXTERNAL_ARTISTS сбора плейлистов.")

            await asyncio.sleep(5)  # Задержка для загрузки

            # 1. Пропускаем рекламу (дважды, на случай задержки)
            await self.skip_ad_action(params)
            await self.skip_ad_action(params)

            # 2. Нажимаем на кнопку поиска
            await self.click_search_action(params)

            # 3. Выбираем нашего артиста и вводим его в строку поиска
            await self.select_artist_action({
                "our_artist_weight": 0,
                "external_artist_weight": 100
            })

            # 4. Ждем загрузки результатов поиска
            await asyncio.sleep(params.get("wait_after_search", 4))

            # 5. Открываем вкладку альбомов
            await self.open_albums_tab_action(params)

            # 6. Ждем загрузки вкладки альбомов
            await asyncio.sleep(params.get("wait_after_albums", 2))

            # 7. Выбираем случайный альбом и запускаем его воспроизведение
            await self.select_random_album_action(params)

            # 8. Собираем треки из плейлиста
            await self.collect_playlist_tracks_action(params)

            logging.info("[EXTERNAL_PLAYLIST_COLLECT] Рабочий процесс сбора плейлистов завершен успешно.")

        except Exception as e:
            logging.error(f"[EXTERNAL_PLAYLIST_COLLECT] Ошибка выполнения рабочего процесса: {e}")

    async def playlist_collection_workflow(self, params):
        """
        Интеллектуальная функция для управления процессом сбора плейлистов.
        Выполняет все действия последовательно, с возможностью добавления логики.
        """
        try:
            logging.info("[PLAYLIST_COLLECTION_WORKFLOW] Начало выполнения рабочего процесса сбора плейлистов.")

            # 1. Проверяем первый запуск за день
            is_first_launch = await self.check_first_launch_action(params)
            if is_first_launch:
                logging.info("[PLAYLIST_COLLECTION_WORKFLOW] Это первый запуск за сегодня.")

            # 2. Проверяем наличие файла анализа
            analysis_results_path = "/app/DCA_configs/analysis_results.json"
            if not os.path.exists(analysis_results_path):
                logging.info("[PLAYLIST_COLLECTION_WORKFLOW] Файл анализа не найден.")
                if random.random() < 0.3:  # Вероятность 30%
                    await self.run_def_collection_action(params)
                else:
                    logging.info("[PLAYLIST_COLLECTION_WORKFLOW] Выполнение прервано (70%).")
                    return

            else:
                # 3. Загружаем данные из файла анализа
                with open(analysis_results_path, "r", encoding="utf-8") as file:
                    analysis_results = json.load(file)

                total_tracks = analysis_results.get("total_tracks", 0)
                balance_status = analysis_results.get("balance_status", "")
                logging.info(f"[PLAYLIST_COLLECTION_WORKFLOW] total_tracks={total_tracks}, balance_status={balance_status}")

                # 4. Проверяем общее количество треков
                if total_tracks < 50:
                    logging.info("[PLAYLIST_COLLECTION_WORKFLOW] Общее количество треков < 50. Запускаем сбор по умолчанию.")
                    await self.run_def_collection_action(params)
                    return

                # 5. Проверяем балансировку
                if balance_status == "Балансировка не требуется":
                    if random.random() < 0.3:  # Вероятность 30%
                        await self.run_def_collection_action(params)
                    else:
                        logging.info("[PLAYLIST_COLLECTION_WORKFLOW] Выполнение прервано (70%).")
                        return

                elif balance_status == "Требуется балансировка":
                    tracks_to_add = analysis_results.get("tracks_to_add", {})
                    tracks_count = tracks_to_add.get("count", 0)

                    if tracks_count > 0:  # Проверяем, что количество треков больше 0
                        if tracks_to_add.get("type") == "external_artists":
                            logging.info("[PLAYLIST_COLLECTION_WORKFLOW] Дисбаланс в сторону наших исполнителей. Добавляем внешние треки.")
                            await self.run_external_artists_collection_action(params)
                        elif tracks_to_add.get("type") == "our_artists":
                            logging.info("[PLAYLIST_COLLECTION_WORKFLOW] Дисбаланс в сторону внешних исполнителей. Добавляем наши треки.")
                            await self.run_our_artists_collection_action(params)
                    else:
                        logging.info("[PLAYLIST_COLLECTION_WORKFLOW] Количество треков для добавления = 0. Действие не требуется.")

            # 6. Возвращаемся к плейлисту Liked Music
            await self.return_to_liked_music_action(params)

        except Exception as e:
            logging.error(f"[PLAYLIST_COLLECTION_WORKFLOW] Ошибка выполнения рабочего процесса: {e}")

############################ [-END-] Сбор Плейлистов ############################

############################ [START] Balancer ############################
    async def save_page_action(self, params):
        """
        Сохраняет страницу через Ctrl+S с использованием темплейтов для взаимодействия с элементами.
        """
        if await self.check_analysis_file_age(params):
            # Файл отсутствует или устарел
            logging.info("[CALLER_FUNCTION] Продолжаем выполнение.")
        else:
            # Файл актуален, прерываем выполнение
            logging.info("[CALLER_FUNCTION] Выполнение прервано из-за актуальности анализа.")
            return

        try:
            threshold = params.get("threshold", 0.9)  # Порог совпадения по умолчанию
            logging.info("[SAVE_PAGE_ACTION] Начало выполнения.")

            screen_service = ScreenService()
            mouse_controller = MouseController(self.project_dir)

            # Шаг 0: Удаление старого файла, если он существует
            save_path = "/app/DCA_config/balancer.txt"
            if os.path.exists(save_path):
                os.remove(save_path)
                logging.info(f"[SAVE_PAGE_ACTION] Удален существующий файл: {save_path}")

            # Проверяем наличие темплейта liked_music и нажимаем на него
            if screen_service.is_template_on_screen("liked_music", threshold):
                logging.info("[RETURN_TO_LIKED_MUSIC_ACTION] Темплейт 'liked_music' найден.")
                template_location = screen_service.get_template_location("liked_music", threshold)

                if template_location:
                    x, y, width, height = template_location
                    target_x = x + width // 2
                    target_y = y + height // 2

                    # Нажатие на темплейт 'liked_music'
                    mouse_controller.move_to(target_x, target_y)
                    mouse_controller.click()
                    logging.info("[RETURN_TO_LIKED_MUSIC_ACTION] Нажатие на темплейт 'liked_music'.")
                else:
                    logging.error("[RETURN_TO_LIKED_MUSIC_ACTION] Не удалось определить координаты темплейта 'liked_music'.")
                    return
            else:
                logging.error("[RETURN_TO_LIKED_MUSIC_ACTION] Темплейт 'liked_music' не найден.")
                return
            
            
            await asyncio.sleep(4)  # Задержка для загрузки


            # Шаг 1: Вызов окна сохранения (Ctrl+S)
            pyautogui.hotkey("ctrl", "s")
            logging.info("[SAVE_PAGE_ACTION] Окно сохранения вызвано.")
            await asyncio.sleep(3)  # Задержка для отображения окна

            # Шаг 2: Нажатие на анкорное поле для ввода имени файла (blncr_name_ancor)
            if screen_service.is_template_on_screen("blncr_name_ancor", threshold):
                logging.info("[SAVE_PAGE_ACTION] Темплейт 'blncr_name_ancor' найден. Нажимаем правой кнопкой.")
                if not screen_service.interact_with_template_right_click("blncr_name_ancor", mouse_controller, threshold):
                    logging.error("[SAVE_PAGE_ACTION] Не удалось нажать правой кнопкой на 'blncr_name_ancor'.")
                    return
            else:
                logging.error("[SAVE_PAGE_ACTION] Темплейт 'blncr_name_ancor' не найден.")
                return


            # Шаг 3: Максимизация окна сохранения, если необходимо (blncr_maximise)
            if screen_service.is_template_on_screen("blncr_maximise", threshold):
                logging.info("[SAVE_PAGE_ACTION] Темплейт 'blncr_maximise' найден. Выполняем нажатие.")
                screen_service.interact_with_template("blncr_maximise", mouse_controller, threshold)

            # Шаг 4: Выбор формата файла через выпадающий список (blncr_arrow.down)
            if screen_service.is_template_on_screen("blncr_arrow.down", threshold):
                logging.info("[SAVE_PAGE_ACTION] Темплейт 'blncr_arrow.down' найден. Выполняем нажатие.")
                if not screen_service.interact_with_template("blncr_arrow.down", mouse_controller, threshold):
                    logging.error("[SAVE_PAGE_ACTION] Не удалось нажать на 'blncr_arrow.down'.")
                    return
                
                await asyncio.sleep(2)  # Задержка для загрузки
                # Клавишу вверх для отображения всего списка
                pyautogui.hotkey("down")
                await asyncio.sleep(2)  # Задержка для загрузки
                pyautogui.hotkey("down")

                # Нажатие на 'blncr_textfiles'
                if not screen_service.interact_with_template("blncr_textfiles", mouse_controller, threshold):
                    logging.error("[SAVE_PAGE_ACTION] Не удалось нажать на 'blncr_textfiles'.")
                    return
            else:
                logging.error("[SAVE_PAGE_ACTION] Темплейт 'blncr_textfiles' не найден.")
                return

            # Шаг 5: Ввод пути сохранения файла (blncr_input)
            if screen_service.is_template_on_screen("blncr_input", threshold):
                logging.info("[SAVE_PAGE_ACTION] Темплейт 'blncr_input' найден. Выполняем ввод пути.")

                pyautogui.hotkey("ctrl", "a")
                logging.info("[SAVE_PAGE_ACTION] Выполняем выбрать всё.")
                await asyncio.sleep(1)  # Задержка для отображения окна

                pyautogui.typewrite("/app/DCA/balancer.txt")
                logging.info("[SAVE_PAGE_ACTION] Введен путь сохранения: /app/DCA/balancer.txt")
            else:
                logging.error("[SAVE_PAGE_ACTION] Темплейт 'blncr_input' не найден.")
                return

            # Шаг 6: Подтверждение сохранения
            pyautogui.press("enter")
            logging.info("[SAVE_PAGE_ACTION] Подтверждение сохранения выполнено.")

            # Шаг 7: Проверка наличия файла
            await asyncio.sleep(3)  # Небольшая задержка для завершения сохранения
            if os.path.exists(save_path):
                logging.info(f"[SAVE_PAGE_ACTION] Файл успешно сохранен: {save_path}")
            else:
                logging.error("[SAVE_PAGE_ACTION] Файл не найден после сохранения.")

        except Exception as e:
            logging.error(f"[SAVE_PAGE_ACTION] Ошибка: {e}")

    async def parse_liked_tracks_action(self, params):
        """
        Анализирует треки в файле balancer.txt, вычисляет соотношение наших и чужих треков и выводит результаты в консоль.
        :param params: Параметры действия, включающие путь к белому списку и путь к файлу balancer.txt.
        """
        if await self.check_analysis_file_age(params):
            # Файл отсутствует или устарел
            logging.info("[CALLER_FUNCTION] Продолжаем выполнение.")
        else:
            # Файл актуален, прерываем выполнение
            logging.info("[CALLER_FUNCTION] Выполнение прервано из-за актуальности анализа.")
            return

        try:
            # Параметры
            white_list_path = params.get("white_list_path", "/app/DCA/configs/white_list.json")
            balancer_file_path = params.get("balancer_file_path", "/app/DCA/balancer.txt")
            output_config_path = "/app/DCA_configs/analysis_results.json"

            # Проверка существования файла balancer.txt
            if not os.path.exists(balancer_file_path):
                logging.error(f"[PARSE_LIKED_TRACKS_ACTION] Файл {balancer_file_path} не найден.")
                return

            # Загрузка белого списка
            if not os.path.exists(white_list_path):
                logging.error(f"[PARSE_LIKED_TRACKS_ACTION] Файл белого списка {white_list_path} не найден.")
                return

            with open(white_list_path, "r", encoding="utf-8") as file:
                white_list = json.load(file)

            our_artists = set(white_list.get("electronic", {}).get("our_artists", []))

            # Чтение файла balancer.txt
            with open(balancer_file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            # Извлечение общего количества треков в плейлисте
            total_tracks_match = next((line for line in lines if "songs•" in line), None)
            if total_tracks_match:
                total_tracks = int(re.search(r"\d+(?=\s+songs•)", total_tracks_match).group())
            else:
                total_tracks = 0

            # Подсчёт упоминаний наших артистов
            our_tracks = 0
            for line in lines:
                for artist in our_artists:
                    if artist in line:
                        our_tracks += 1

            # Расчёт соотношения
            ratio = (our_tracks / total_tracks * 100) if total_tracks > 0 else 0.0

            # Сохранение результатов в конфигурационный файл
            results = {
                "total_tracks": total_tracks,
                "our_tracks": our_tracks,
                "ratio": round(ratio, 2),
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            os.makedirs(os.path.dirname(output_config_path), exist_ok=True)
            with open(output_config_path, "w", encoding="utf-8") as outfile:
                json.dump(results, outfile, ensure_ascii=False, indent=4)

            # Вывод результатов
            logging.info(f"[PARSE_LIKED_TRACKS_ACTION] Анализ завершён и сохранён в {output_config_path}.")
            print(f"Общее количество треков: {total_tracks}")
            print(f"Наши треки: {our_tracks}")
            print(f"Процент наших треков: {ratio:.2f}%")
            print(f"Результаты сохранены в файл: {output_config_path}")

        except Exception as e:
            logging.error(f"[PARSE_LIKED_TRACKS_ACTION] Ошибка: {e}")
            print(f"Ошибка анализа треков: {e}")

        try:
            # Параметры
            analysis_results_path = "/app/DCA_configs/analysis_results.json"
            ideal_balance_path = "/app/DCA/configs/ideal_balance.json"

            # Проверка существования файлов
            if not os.path.exists(analysis_results_path):
                logging.error(f"[ANALYZE_TRACK_BALANCE] Файл {analysis_results_path} не найден.")
                return

            if not os.path.exists(ideal_balance_path):
                logging.error(f"[ANALYZE_TRACK_BALANCE] Файл {ideal_balance_path} не найден.")
                return

            # Загрузка данных
            with open(analysis_results_path, "r", encoding="utf-8") as file:
                analysis_results = json.load(file)

            with open(ideal_balance_path, "r", encoding="utf-8") as file:
                ideal_balance_data = json.load(file)

            # Извлечение данных из файлов
            total_tracks = analysis_results.get("total_tracks", 0)
            our_tracks = analysis_results.get("our_tracks", 0)

            ideal_balance = ideal_balance_data.get("ideal_balance", {})
            ideal_our_ratio = ideal_balance.get("our_artists", 0)
            ideal_external_ratio = ideal_balance.get("external_artists", 0)

            # Проверка корректности данных
            if ideal_our_ratio + ideal_external_ratio != 100:
                logging.error("[ANALYZE_TRACK_BALANCE] Некорректное соотношение в ideal_balance.json.")
                return

            # Расчёт текущего и идеального соотношения
            current_our_ratio = (our_tracks / total_tracks * 100) if total_tracks > 0 else 0.0
            deviation_allowed = 5  # Допустимое отклонение в процентах

            # Анализ соответствия
            if abs(current_our_ratio - ideal_our_ratio) <= deviation_allowed:
                balance_status = "Балансировка не требуется"
                tracks_to_add = None
            else:
                balance_status = "Требуется балансировка"
                ideal_our_tracks = int(total_tracks * ideal_our_ratio / 100)
                ideal_external_tracks = total_tracks - ideal_our_tracks

                if current_our_ratio > ideal_our_ratio:
                    tracks_to_add = {
                        "type": "external_artists",
                        "count": max(0, ideal_external_tracks - (total_tracks - our_tracks))
                    }
                else:
                    tracks_to_add = {
                        "type": "our_artists",
                        "count": max(0, ideal_our_tracks - our_tracks)
                    }

            # Дополнение результатов
            analysis_results.update({
                "balance_status": balance_status,
                "tracks_to_add": tracks_to_add,
                "ideal_our_ratio": ideal_our_ratio,
                "current_our_ratio": round(current_our_ratio, 2),
                "deviation_allowed": deviation_allowed
            })

            # Сохранение обновленных результатов
            with open(analysis_results_path, "w", encoding="utf-8") as file:
                json.dump(analysis_results, file, ensure_ascii=False, indent=4)

            # Логирование
            logging.info(f"[ANALYZE_TRACK_BALANCE] Анализ завершён. Результаты сохранены в {analysis_results_path}.")
            print(f"Балансировка: {balance_status}")
            if tracks_to_add:
                print(f"Необходимо добавить {tracks_to_add['count']} треков типа {tracks_to_add['type']}.")

        except Exception as e:
            logging.error(f"[ANALYZE_TRACK_BALANCE] Ошибка: {e}")
            print(f"Ошибка анализа баланса треков: {e}")

    async def check_analysis_file_age(self, params):
        """
        Проверяет наличие и возраст файла /app/DCA_configs/analysis_results.json.
        Если файл отсутствует или его возраст >= 7 дней, выводит сообщение.
        Если возраст < 7 дней, прерывает выполнение вызывающей функции.
        :param params: Параметры действия (не используются).
        :return: True, если файл отсутствует или устарел; False, если файл актуален.
        """
        try:
            # Путь к файлу анализа
            analysis_results_path = "/app/DCA_configs/analysis_results.json"

            # Проверяем существование файла
            if not os.path.exists(analysis_results_path):
                logging.warning("[CHECK_ANALYSIS_FILE_AGE] Файл отсутствует.")
                print("Файл анализа отсутствует. Требуется выполнить новый анализ.")
                return True

            # Чтение файла
            with open(analysis_results_path, "r", encoding="utf-8") as file:
                analysis_results = json.load(file)

            # Получение даты последнего обновления
            last_updated = analysis_results.get("last_updated")
            if not last_updated:
                logging.warning("[CHECK_ANALYSIS_FILE_AGE] Дата обновления отсутствует в файле.")
                print("Дата последнего обновления отсутствует. Требуется выполнить новый анализ.")
                return True

            # Проверка возраста файла
            last_updated_date = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S")
            age_in_days = (datetime.now() - last_updated_date).days

            if age_in_days >= 7:
                logging.warning(f"[CHECK_ANALYSIS_FILE_AGE] Файл устарел ({age_in_days} дней).")
                print(f"Файл анализа устарел ({age_in_days} дней). Требуется выполнить новый анализ.")
                return True

            # Файл актуален
            logging.info(f"[CHECK_ANALYSIS_FILE_AGE] Файл актуален ({age_in_days} дней).")
            return False

        except Exception as e:
            logging.error(f"[CHECK_ANALYSIS_FILE_AGE] Ошибка: {e}")
            print(f"Ошибка проверки файла анализа: {e}")
            return True

############################ [-END-] Balancer ############################

############################ [START] Fingerprint ############################
    async def generate_user_profile_action(self, params):
        """
        Проверяет, имеется ли уже сгенерированный профиль в каталоге.
        Если профиль отсутствует, генерирует новый.
        Если в профиле отсутствуют данные, добавляет недостающие.
        """
        try:
            # Заданные пути
            config_path = "/app/DCA/configs/generation_config.json"  # Путь к конфигурации
            profile_dir = "/app/DCA_configs"  # Каталог для хранения профилей
            profile_path = os.path.join(profile_dir, "user_profile.json")  # Путь к профилю

            # Проверка наличия файла конфигурации
            if not os.path.exists(config_path):
                logging.error(f"Файл конфигурации {config_path} не найден.")
                return

            # Загрузка конфигурации генерации
            try:
                with open(config_path, "r", encoding="utf-8") as config_file:
                    config = json.load(config_file)
                    if not isinstance(config, dict):
                        raise ValueError("Файл конфигурации должен быть JSON-объектом.")
            except json.JSONDecodeError as e:
                logging.error(f"Ошибка чтения JSON из файла конфигурации: {e}")
                return
            except ValueError as e:
                logging.error(f"Ошибка в формате файла конфигурации: {e}")
                return

            # Создание каталога для профилей, если он не существует
            os.makedirs(profile_dir, exist_ok=True)

            # Проверка существующего профиля
            if os.path.exists(profile_path):
                try:
                    with open(profile_path, "r", encoding="utf-8") as profile_file:
                        profile = json.load(profile_file)
                        if not isinstance(profile, dict):
                            raise ValueError("Файл профиля должен быть JSON-объектом.")
                except json.JSONDecodeError as e:
                    logging.error(f"Ошибка чтения JSON из файла профиля: {e}")
                    return
                except ValueError as e:
                    logging.error(f"Ошибка в формате файла профиля: {e}")
                    return

                # Проверка на наличие недостающих данных
                updated = False
                for key, values in config.items():
                    if key not in profile or not profile[key]:
                        if isinstance(values, list) and values:
                            profile[key] = random.choice(values)
                            logging.info(f"Добавлено недостающее поле '{key}' в профиль.")
                            updated = True
                        else:
                            logging.warning(f"Пропущено поле '{key}': значения отсутствуют в конфигурации.")

                # Сохранение обновленного профиля
                if updated:
                    with open(profile_path, "w", encoding="utf-8") as profile_file:
                        json.dump(profile, profile_file, ensure_ascii=False, indent=4)
                    logging.info(f"Профиль обновлен: {profile_path}")
                else:
                    logging.info(f"Профиль уже содержит все необходимые данные: {profile_path}")
            else:
                # Генерация нового профиля
                profile = {}
                for key, values in config.items():
                    if isinstance(values, list) and values:
                        profile[key] = random.choice(values)
                    else:
                        logging.warning(f"Пропущено поле '{key}': значения отсутствуют в конфигурации.")

                with open(profile_path, "w", encoding="utf-8") as profile_file:
                    json.dump(profile, profile_file, ensure_ascii=False, indent=4)
                logging.info(f"Создан новый профиль: {profile_path}")

        except Exception as e:
            logging.error(f"Ошибка при обработке профиля: {e}")

############################ [-END-] Fingerprint ############################