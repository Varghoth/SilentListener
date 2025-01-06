import random
import pyautogui
import json
import time
import math
import pyautogui
import json
import logging


class MouseController:
    def __init__(self, config_path):
        self.load_config(config_path)

    def load_config(self, config_path):
        """
        Загружает конфигурацию из файла.
        """
        try:
            with open(config_path, "r", encoding="utf-8") as file:
                self.config = json.load(file)
        except Exception as e:
            logging.error(f"Ошибка загрузки конфигурации: {e}")
            self.config = {"base_speed": 0.1}  # Значения по умолчанию

    def _generate_bezier_control_points(self, start_x, start_y, end_x, end_y):
        """
        Генерирует контрольные точки для кривой Безье между начальной и конечной точками.
        """
        # Случайные точки между началом и концом для кривой
        control_x1 = random.randint(min(start_x, end_x), max(start_x, end_x))
        control_y1 = random.randint(min(start_y, end_y), max(start_y, end_y))
        control_x2 = random.randint(min(start_x, end_x), max(start_x, end_x))
        control_y2 = random.randint(min(start_y, end_y), max(start_y, end_y))

        return [(start_x, start_y), (control_x1, control_y1), (control_x2, control_y2), (end_x, end_y)]

    def _generate_bezier_curve(self, control_points, steps):
        """
        Вычисляет точки на кривой Безье с заданными контрольными точками.
        :param control_points: Список контрольных точек.
        :param steps: Количество точек на кривой.
        :return: Список точек [(x1, y1), (x2, y2), ...].
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


    def move_to(self, x, y, template_size=(0, 0)):
        """
        Плавное перемещение мыши к заданной точке (x, y) по случайной кривой Безье.
        После завершения движения выполняется корректировочное движение.
        """
        screen_width, screen_height = pyautogui.size()

        # Учитываем границы экрана
        x = max(0, min(screen_width - 1, x))
        y = max(0, min(screen_height - 1, y))

        # Получаем текущую позицию мыши
        current_x, current_y = pyautogui.position()

        # Вычисляем расстояние до конечной точки
        distance = math.sqrt((x - current_x) ** 2 + (y - current_y) ** 2)

        # Динамическое количество шагов
        steps = max(10, int(distance / 20))  # Минимум 10 шагов, 1 шаг на каждые 20 пикселей
        base_speed = self.config.get("base_speed", 0.01)

        # Генерируем контрольные точки для кривой Безье
        control_points = self._generate_bezier_control_points(current_x, current_y, x, y)

        # Вычисляем точки на кривой Безье
        trajectory = self._generate_bezier_curve(control_points, steps)

        # Двигаем мышь по траектории
        for point_x, point_y in trajectory:
            pyautogui.moveTo(point_x, point_y, duration=base_speed / steps)

        logging.info(f"Основное движение мыши завершено. Конечная точка: ({x}, {y}).")

        # Корректировочное движение
        self._adjust_position(x, y, template_size)

    def _adjust_position(self, x, y, template_size):
        """
        Корректировочное движение к произвольной точке в пределах 5%-25% ширины шаблона.
        """
        template_width, _ = template_size

        # Рассчитываем смещение в пределах 5%-25% ширины шаблона
        offset_x = random.uniform(-template_width * 0.25, template_width * 0.25)
        offset_y = random.uniform(-template_width * 0.25, template_width * 0.25)

        # Ограничиваем смещение по минимальному радиусу 5%
        distance = math.sqrt(offset_x**2 + offset_y**2)
        if distance < template_width * 0.05:
            scale = (template_width * 0.05) / distance
            offset_x *= scale
            offset_y *= scale

        # Конечные координаты корректировочного движения
        final_x = int(x + offset_x)
        final_y = int(y + offset_y)

        # Движение в два шага
        current_x, current_y = pyautogui.position()
        for i in range(2):
            t = (i + 1) / 2
            intermediate_x = int(current_x + (final_x - current_x) * t)
            intermediate_y = int(current_y + (final_y - current_y) * t)
            pyautogui.moveTo(intermediate_x, intermediate_y, duration=self.config.get("base_speed", 0.01) / 2)

        logging.info(f"Корректировочное движение завершено. Конечная точка: ({final_x}, {final_y}).")



    def click(self):
        """
        Симулирует клик мыши.
        """
        pyautogui.click()
        logging.info("Клик мыши выполнен.")

