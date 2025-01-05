import random
import pyautogui
import json  # Добавляем импорт
import time
import math

class MouseController:
    def __init__(self, config_path):
        self.load_config(config_path)

    def load_config(self, config_path):
        with open(config_path, "r", encoding="utf-8") as file:
            self.config = json.load(file)

    def move_to(self, x, y, template_size=(0, 0)):
        """
        Реалистичное движение мыши к заданной точке (x, y) через траекторию.
        """
        current_x, current_y = pyautogui.position()
        template_width, template_height = template_size

        # Генерация погрешностей для основного движения
        offset_range = self.config["offset_range_main"]
        target_x = x + random.randint(int(template_width * offset_range[0]), int(template_width * offset_range[1]))
        target_y = y + random.randint(int(template_height * offset_range[0]), int(template_height * offset_range[1]))

        # Основное движение
        self._bezier_move(
            current_x,
            current_y,
            target_x,
            target_y,
            num_points=random.randint(3, 5),
            speed=self.config["base_speed"],
        )

        # Генерация погрешностей для корректировочного движения
        offset_range = self.config["offset_range_correction"]
        target_x = x + random.randint(int(template_width * offset_range[0]), int(template_width * offset_range[1]))
        target_y = y + random.randint(int(template_height * offset_range[0]), int(template_height * offset_range[1]))

        # Корректировочное движение
        self._bezier_move(
            *pyautogui.position(),
            target_x,
            target_y,
            num_points=random.randint(2, 3),
            speed=self.config["correction_speed"],
        )

    def _bezier_move(self, start_x, start_y, end_x, end_y, num_points, speed):
        """
        Движение мыши по кривой Безье.
        """
        # Генерация контрольных точек
        control_points = [(start_x, start_y)]
        for _ in range(num_points - 2):
            control_x = random.randint(min(start_x, end_x), max(start_x, end_x))
            control_y = random.randint(min(start_y, end_y), max(start_y, end_y))
            control_points.append((control_x, control_y))
        control_points.append((end_x, end_y))

        # Вычисление траектории
        trajectory = self._generate_bezier_curve(control_points)

        # Движение мыши
        for i, (x, y) in enumerate(trajectory):
            duration = speed / len(trajectory) * (1.5 if i / len(trajectory) > 0.7 else 1)  # Ускорение к концу
            pyautogui.moveTo(x, y, duration=duration)

    def _generate_bezier_curve(self, control_points):
        """
        Генерация траектории на основе контрольных точек.
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

        return [bezier_point(t / 100, control_points) for t in range(101)]

    def click(self):
        """
        Симулирует клик мыши с задержкой.
        """
        delay = random.uniform(*self.config["delay_before_click"])
        time.sleep(delay)
        pyautogui.click()
