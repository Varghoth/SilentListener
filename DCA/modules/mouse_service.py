import random
import pyautogui
import json
import logging
import math
import time
import os

class MouseController:
    def __init__(self, project_dir):
        """
        Инициализация MouseController.
        Загружает конфигурацию из DCA_config/config.json или создает ее случайным образом.
        """
        self.project_dir = os.path.abspath(project_dir)  # Абсолютный путь к проекту
        self.config_dir = os.path.join(project_dir, "DCA_config")
        self.config_path = os.path.join(self.config_dir, "movement_profile.json")
        self.load_or_generate_config()

    def load_or_generate_config(self):
        """
        Загружает конфигурацию из файла или генерирует новую.
        """
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as file:
                    self.config = json.load(file)
                    logging.info(f"Конфигурация загружена из {self.config_path}.")
            except Exception as e:
                logging.error(f"Ошибка загрузки конфигурации: {e}")
                self.generate_random_config()
        else:
            self.generate_random_config()

    def generate_random_config(self):
        """
        Генерирует случайную конфигурацию и сохраняет ее в файл.
        """
        self.config = {
            "delay": {"min": round(random.uniform(0.1, 0.3), 2), "max": round(random.uniform(0.4, 0.7), 2)},
            "bezier_curve_strength": {"min": round(random.uniform(0.2, 0.5), 2), "max": round(random.uniform(0.6, 0.8), 2)},
            "steps_main": {"min": random.randint(10, 20), "max": random.randint(25, 50)},
            "steps_correction": {"min": random.randint(2, 3), "max": random.randint(4, 6)},
            "template_offset": {"min": round(random.uniform(0.05, 0.1), 2), "max": round(random.uniform(0.2, 0.3), 2)},
            "scroll_amount": {
                "min": random.randint(1, 5),
                "max": random.randint(6, 15)
            },
            "scroll_delay": {
                "min": round(random.uniform(0.1, 0.3), 2),
                "max": round(random.uniform(0.4, 0.7), 2)
            }
        }
        os.makedirs(self.config_dir, exist_ok=True)
        try:
            with open(self.config_path, "w", encoding="utf-8") as file:
                json.dump(self.config, file, indent=4, ensure_ascii=False)
                logging.info(f"Сгенерирована новая конфигурация и сохранена в {self.config_path}.")
        except Exception as e:
            logging.error(f"Ошибка при сохранении конфигурации: {e}")

    def _random_value(self, param_name):
        """
        Возвращает случайное значение в пределах, указанных в конфигурации.
        """
        param = self.config.get(param_name, {"min": 0, "max": 1})
        return random.uniform(param["min"], param["max"])

    def move_to(self, x, y, template_size=(0, 0)):
        """
        Плавное перемещение мыши к заданной точке (x, y) с учетом кривой Безье.
        """
        screen_width, screen_height = pyautogui.size()

        # Учитываем границы экрана
        x = max(0, min(screen_width - 1, x))
        y = max(0, min(screen_height - 1, y))

        # Получаем текущую позицию мыши
        current_x, current_y = pyautogui.position()

        # Основное движение
        steps_main = int(self._random_value("steps_main"))
        base_speed = self.config.get("base_speed", 0.01)
        control_points = self._generate_bezier_control_points(current_x, current_y, x, y)
        trajectory = self._generate_bezier_curve(control_points, steps_main)

        for point_x, point_y in trajectory:
            pyautogui.moveTo(point_x, point_y, duration=base_speed / steps_main)

        logging.info(f"Основное движение завершено. Конечная точка: ({x}, {y}).")

        # Корректировочное движение
        self._adjust_position(x, y, template_size)

    def _adjust_position(self, x, y, template_size):
        """
        Корректировочное движение к случайной точке в пределах 5%-25% ширины шаблона.
        """
        template_width, _ = template_size

        # Рассчитываем смещение в пределах заданного процента
        min_offset = self.config["template_offset"]["min"]
        max_offset = self.config["template_offset"]["max"]
        offset_x = random.uniform(-template_width * max_offset, template_width * max_offset)
        offset_y = random.uniform(-template_width * max_offset, template_width * max_offset)

        # Ограничиваем минимальный радиус смещения
        distance = math.sqrt(offset_x**2 + offset_y**2)
        if distance < template_width * min_offset:
            scale = (template_width * min_offset) / distance
            offset_x *= scale
            offset_y *= scale

        # Корректировочные шаги
        steps_correction = int(self._random_value("steps_correction"))
        final_x = int(x + offset_x)
        final_y = int(y + offset_y)

        current_x, current_y = pyautogui.position()
        for i in range(steps_correction):
            t = (i + 1) / steps_correction
            intermediate_x = int(current_x + (final_x - current_x) * t)
            intermediate_y = int(current_y + (final_y - current_y) * t)
            pyautogui.moveTo(intermediate_x, intermediate_y, duration=self.config.get("base_speed", 0.01) / steps_correction)

        logging.info(f"Корректировочное движение завершено. Конечная точка: ({final_x}, {final_y}).")

    def _generate_bezier_control_points(self, start_x, start_y, end_x, end_y):
        """
        Генерирует контрольные точки для кривой Безье между начальной и конечной точками.
        """
        curve_strength = self._random_value("bezier_curve_strength")
        control_x1 = int(start_x + (end_x - start_x) * curve_strength)
        control_y1 = random.randint(min(start_y, end_y), max(start_y, end_y))
        control_x2 = int(end_x - (end_x - start_x) * curve_strength)
        control_y2 = random.randint(min(start_y, end_y), max(start_y, end_y))

        return [(start_x, start_y), (control_x1, control_y1), (control_x2, control_y2), (end_x, end_y)]

    def _generate_bezier_curve(self, control_points, steps):
        """
        Вычисляет точки на кривой Безье с заданными контрольными точками.
        """
        def bezier_point(t, points):
            while len(points) > 1:
                points = [
                    (
                        (1 - t) * p1[0] + t * p2[0],
                        (1 - t) * p1[1] + t * p2[1],
                    )
                    for p1, p2 in zip(points[:-1], points[1:])
                ]
            return points[0]

        return [bezier_point(t / steps, control_points) for t in range(steps)]

    def click(self):
        """
        Симулирует клик мыши.
        """
        delay = self._random_value("delay")
        time.sleep(delay)
        pyautogui.click()
        logging.info(f"Клик мыши выполнен с задержкой {delay:.2f} сек.")

    def scroll(self, direction="down", amount=None):
        """
        Эмулирует прокрутку колесика мыши.
        :param direction: Направление прокрутки ('up' или 'down').
        :param amount: Количество "щелчков" прокрутки (если None, определяется случайно).
        """
        # Устанавливаем случайное количество прокруток, если не задано
        if amount is None:
            amount = random.randint(
                int(self.config.get("scroll_amount", {}).get("min", 1)),
                int(self.config.get("scroll_amount", {}).get("max", 10))
            )

        # Определяем направление
        multiplier = 1 if direction == "down" else -1
        scroll_amount = amount * multiplier

        # Прокрутка
        pyautogui.scroll(scroll_amount)
        logging.info(f"Прокрутка {direction} на {amount} шагов.")
        # Добавляем случайную задержку для реалистичности
        delay = random.uniform(
            self.config.get("scroll_delay", {}).get("min", 0.2),
            self.config.get("scroll_delay", {}).get("max", 0.5)
        )
        time.sleep(delay)

    def precise_scroll(self, direction="down", steps=10, delay_between_steps=(0.05, 0.2)):
        """
        Прокрутка списков с фиксированным количеством шагов и задержками между шагами.
        :param direction: Направление прокрутки ('up' или 'down').
        :param steps: Количество шагов.
        :param delay_between_steps: Кортеж с минимальной и максимальной задержкой между шагами.
        """
        multiplier = 1 if direction == "down" else -1
        for _ in range(steps):
            pyautogui.scroll(multiplier)
            delay = random.uniform(*delay_between_steps)
            time.sleep(delay)
        logging.info(f"Точная прокрутка {direction} на {steps} шагов.")
