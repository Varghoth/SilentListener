import os
import cv2
import numpy as np
import pyautogui
import logging

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