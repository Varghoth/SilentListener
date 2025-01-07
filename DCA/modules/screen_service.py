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
        Ищет шаблон на экране, вычисляет его центр и кликает по нему.
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

                # Выполняем действия
                self.logger.info(f"Шаблон найден. Центр: ({center_x}, {center_y}), совпадение: {max_val}")
                mouse_controller.move_to(center_x, center_y)
                mouse_controller.click()
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
