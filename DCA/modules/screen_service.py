import os
import cv2
import numpy as np
import pyautogui
import logging
import random
import math
from modules.mouse_service import MouseController

class ScreenService:
    """
    Сервис для работы с экраном и шаблонами.
    """

    def __init__(self, base_template_path="/app/DCA/templates"):
        self.logger = logging.getLogger("ScreenService")
        self.base_template_path = base_template_path  # Базовый путь к шаблонам
        self.screen_width, self.screen_height = pyautogui.size()  # Инициализация размеров экрана

    def get_screen_width(self):
        return self.screen_width

    def get_screen_height(self):
        return self.screen_height
    
    def capture_screen(self):
        """
        Делает скриншот экрана и возвращает его в формате numpy.ndarray (в градациях серого).
        """
        try:
            screenshot = pyautogui.screenshot()
            #return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY) # Градации серого (GRAY)
            return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)   # Цветной (BGR)
        except Exception as e:
            self.logger.error(f"Ошибка при захвате экрана: {e}")
            return None

    def load_templates(self, folder_name):
        """
        Загружает все шаблоны из указанной папки.
        :param folder_name: Имя папки с шаблонами.
        :return: Список шаблонов в формате numpy.ndarray.
        """
        folder_path = os.path.join(self.base_template_path, folder_name)
        self.logger.info(f"Загрузка шаблонов из папки: {folder_path}")
        if not os.path.exists(folder_path):
            self.logger.error(f"Папка не найдена: {folder_path}")
            return []

        templates = []
        invalid_files = []
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".png"):
                full_path = os.path.join(folder_path, file_name)
                #template = cv2.imread(full_path, cv2.IMREAD_GRAYSCALE)  # Градации серого
                template = cv2.imread(full_path, cv2.IMREAD_COLOR)       # Цветное изображение
                if template is not None:
                    templates.append(template)
                else:
                    invalid_files.append(file_name)

        self.logger.info(f"Загружено {len(templates)} шаблонов из {folder_path}.")
        if invalid_files:
            self.logger.warning(f"Не удалось загрузить {len(invalid_files)} файлов: {invalid_files}")
        return templates

    def match_templates_on_screen(self, screen, templates, threshold=0.8):
        """
        Проверяет, соответствует ли один из шаблонов экрану.
        :param screen: numpy.ndarray - скриншот экрана в цвете (BGR).
        :param templates: Список шаблонов.
        :param threshold: Порог совпадения.
        :return: True, если хотя бы один шаблон найден, иначе False.
        """
        for template in templates:
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val >= threshold:
                self.logger.info(f"Шаблон найден на экране. Позиция: {max_loc}, совпадение: {max_val}")
                return True

        self.logger.info("Шаблоны не найдены на экране.")
        return False

    def is_template_on_screen(self, template_name, threshold=0.8):
        """
        Проверяет, присутствует ли на экране шаблон с указанным именем.
        :param template_name: Имя шаблона (папка с шаблонами).
        :param threshold: Порог совпадения.
        :return: True, если хотя бы один шаблон найден, иначе False.
        """
        folder_path = os.path.join(self.base_template_path, template_name)
        templates = self.load_templates(folder_path)
        if not templates:
            self.logger.error(f"[ScreenService] Шаблоны для '{template_name}' не загружены.")
            return False

        screen = self.capture_screen()
        if screen is None:
            self.logger.error("[ScreenService] Ошибка захвата экрана. Проверка завершена.")
            return False

        return self.match_templates_on_screen(screen, templates, threshold)
    
    def interact_with_template(self, template_name, mouse_controller, threshold=0.8):
        """
        Ищет шаблон на экране, вычисляет его центр и кликает по нему с вариативностью.
        """
        templates = self.load_templates(template_name)
        screen = self.capture_screen()

        if not templates or screen is None:
            self.logger.error(f"Шаблоны для '{template_name}' не загружены или экран не захвачен.")
            return False

        for template in templates:
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val >= threshold:
                # Вычисляем центр шаблона
                center_x = max_loc[0] + template.shape[1] // 2
                center_y = max_loc[1] + template.shape[0] // 2

                # Добавляем случайное смещение
                radius_x = template.shape[1] * 0.15  # 10% от ширины шаблона
                radius_y = template.shape[0] * 0.15  # 10% от высоты шаблона
                offset_x = random.uniform(-radius_x, radius_x)
                offset_y = random.uniform(-radius_y, radius_y)

                # Итоговые координаты клика
                target_x = int(center_x + offset_x)
                target_y = int(center_y + offset_y)

                self.logger.info(
                    f"Шаблон найден. Центр: ({center_x}, {center_y}), "
                    f"смещение: ({offset_x:.2f}, {offset_y:.2f}), "
                    f"целевые координаты: ({target_x}, {target_y}), совпадение: {max_val}"
                )

                # Выполняем действия
                mouse_controller.move_to(target_x, target_y)
                mouse_controller.click()
                return True

        self.logger.info(f"Шаблон '{template_name}' не найден.")
        return False

    def target_template(self, template_name, mouse_controller, threshold=0.8): 
        """
        Ищет шаблон на экране, вычисляет его центр и наводит мышь на него с вариативностью.
        """
        templates = self.load_templates(template_name)
        screen = self.capture_screen()

        if not templates or screen is None:
            self.logger.error(f"Шаблоны для '{template_name}' не загружены или экран не захвачен.")
            return False

        for template in templates:
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val >= threshold:
                # Вычисляем центр шаблона
                center_x = max_loc[0] + template.shape[1] // 2
                center_y = max_loc[1] + template.shape[0] // 2

                # Добавляем случайное смещение
                radius_x = template.shape[1] * 0.15  # 15% от ширины шаблона
                radius_y = template.shape[0] * 0.15  # 15% от высоты шаблона
                offset_x = random.uniform(-radius_x, radius_x)
                offset_y = random.uniform(-radius_y, radius_y)

                # Итоговые координаты для наведения
                target_x = int(center_x + offset_x)
                target_y = int(center_y + offset_y)

                self.logger.info(
                    f"Шаблон найден. Центр: ({center_x}, {center_y}), "
                    f"смещение: ({offset_x:.2f}, {offset_y:.2f}), "
                    f"целевые координаты: ({target_x}, {target_y}), совпадение: {max_val}"
                )

                # Наводим мышь
                mouse_controller.move_to(target_x, target_y)

                return True

        self.logger.info(f"Шаблон '{template_name}' не найден.")
        return False

    def get_template_location(self, template_name, threshold=0.8):
        """
        Возвращает координаты верхнего левого угла и размеры найденного шаблона: (x, y, width, height).
        Если шаблон не найден, возвращает None.
        :param template_name: Имя шаблона (папка с шаблонами).
        :param threshold: Порог совпадения.
        :return: (x, y, width, height) или None.
        """
        templates = self.load_templates(template_name)
        screen = self.capture_screen()

        if not templates or screen is None:
            self.logger.error(f"Шаблоны для '{template_name}' не загружены или экран не захвачен.")
            return None

        for template in templates:
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val >= threshold:
                self.logger.info(f"Шаблон найден: {template_name}. Позиция: {max_loc}, совпадение: {max_val}")
                return max_loc[0], max_loc[1], template.shape[1], template.shape[0]

        self.logger.info(f"Шаблон '{template_name}' не найден.")
        return None

    def capture_screen_grayscale(self):
        """
        Делает скриншот экрана и возвращает его в формате numpy.ndarray (в градациях серого).
        """
        try:
            screenshot = pyautogui.screenshot()
            return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
        except Exception as e:
            self.logger.error(f"Ошибка при захвате экрана: {e}")
            return None

    def load_templates_grayscale(self, folder_name):
        """
        Загружает все шаблоны из указанной папки в градациях серого.
        :param folder_name: Имя папки с шаблонами.
        :return: Список шаблонов в формате numpy.ndarray.
        """
        folder_path = os.path.join(self.base_template_path, folder_name)
        self.logger.info(f"Загрузка шаблонов (градации серого) из папки: {folder_path}")
        if not os.path.exists(folder_path):
            self.logger.error(f"Папка не найдена: {folder_path}")
            return []

        templates = []
        invalid_files = []
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".png"):
                full_path = os.path.join(folder_path, file_name)
                template = cv2.imread(full_path, cv2.IMREAD_GRAYSCALE)  # Градации серого
                if template is not None:
                    templates.append(template)
                else:
                    invalid_files.append(file_name)

        self.logger.info(f"Загружено {len(templates)} шаблонов из {folder_path}.")
        if invalid_files:
            self.logger.warning(f"Не удалось загрузить {len(invalid_files)} файлов: {invalid_files}")
        return templates

    def interact_with_template_right_click(self, template_name, mouse_controller, threshold=0.8):
        """
        Ищет шаблон на экране, вычисляет его центр и кликает по нему правой кнопкой мыши.
        :param template_name: Имя шаблона (папка с шаблонами).
        :param mouse_controller: Объект для управления мышью.
        :param threshold: Порог совпадения для поиска шаблона.
        :return: True, если шаблон найден и взаимодействие выполнено, иначе False.
        """
        templates = self.load_templates(template_name)
        screen = self.capture_screen()

        if not templates or screen is None:
            self.logger.error(f"Шаблоны для '{template_name}' не загружены или экран не захвачен.")
            return False

        for template in templates:
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val >= threshold:
                # Вычисляем центр шаблона
                center_x = max_loc[0] + template.shape[1] // 2
                center_y = max_loc[1] + template.shape[0] // 2

                # Добавляем случайное смещение
                radius_x = template.shape[1] * 0.15  # 15% от ширины шаблона
                radius_y = template.shape[0] * 0.15  # 15% от высоты шаблона
                offset_x = random.uniform(-radius_x, radius_x)
                offset_y = random.uniform(-radius_y, radius_y)

                # Итоговые координаты клика
                target_x = int(center_x + offset_x)
                target_y = int(center_y + offset_y)

                self.logger.info(
                    f"Шаблон найден. Центр: ({center_x}, {center_y}), "
                    f"смещение: ({offset_x:.2f}, {offset_y:.2f}), "
                    f"целевые координаты: ({target_x}, {target_y}), совпадение: {max_val}"
                )

                # Выполняем действия правой кнопкой мыши
                mouse_controller.move_to(target_x, target_y)
                mouse_controller.right_click()  # Выполняем правый клик
                return True

        self.logger.info(f"Шаблон '{template_name}' не найден.")
        return False
