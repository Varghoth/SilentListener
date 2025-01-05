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
            return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
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
                template = cv2.imread(full_path, cv2.IMREAD_GRAYSCALE)
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
        :param screen: numpy.ndarray - скриншот экрана в градациях серого.
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
        Ищет шаблон на экране и взаимодействует с ним (двигает мышь и кликает).
        """
        folder_path = os.path.join(self.base_template_path, template_name)
        templates = self.load_templates(folder_path)
        if not templates:
            self.logger.error(f"Шаблоны для '{template_name}' не найдены.")
            return False

        screen = self.capture_screen()
        if screen is None:
            self.logger.error("Ошибка захвата экрана. Взаимодействие завершено.")
            return False

        for template in templates:
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val >= threshold:
                # Вычисляем координаты центра шаблона
                center_x = max_loc[0] + template.shape[1] // 2
                center_y = max_loc[1] + template.shape[0] // 2

                # Добавляем случайное смещение для предпоследнего такта
                radius_min = template.shape[1]  # 100% ширины
                radius_max = template.shape[1] * 2.5  # 250% ширины
                offset_x = random.uniform(-radius_max, radius_max)
                offset_y = random.uniform(-radius_max, radius_max)
                distance = math.sqrt(offset_x**2 + offset_y**2)
                if distance > radius_max or distance < radius_min:
                    scale = radius_max / distance if distance > radius_max else radius_min / distance
                    offset_x *= scale
                    offset_y *= scale

                target_x = int(center_x + offset_x)
                target_y = int(center_y + offset_y)

                # Финальная точка для последнего такта
                final_offset_range = (template.shape[1] * 0.1, template.shape[1] * 0.55)
                final_offset_x = random.uniform(-final_offset_range[1], final_offset_range[1])
                final_offset_y = random.uniform(-final_offset_range[1], final_offset_range[1])
                final_distance = math.sqrt(final_offset_x**2 + final_offset_y**2)
                if final_distance > final_offset_range[1] or final_distance < final_offset_range[0]:
                    scale = final_offset_range[1] / final_distance if final_distance > final_offset_range[1] else final_offset_range[0] / final_distance
                    final_offset_x *= scale
                    final_offset_y *= scale

                final_x = int(center_x + final_offset_x)
                final_y = int(center_y + final_offset_y)

                self.logger.info(f"Шаблон найден. Основная цель: ({target_x}, {target_y}), Финальная цель: ({final_x}, {final_y}), совпадение: {max_val}")

                # Выполняем движение: предпоследний и последний такт
                mouse_controller.move_to(target_x, target_y)
                mouse_controller.move_to(final_x, final_y)

                # Клик мышью после завершения движения
                mouse_controller.click()
                return True

        self.logger.info(f"Шаблон '{template_name}' не найден.")
        return False


