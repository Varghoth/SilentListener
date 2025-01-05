import random
import pyautogui
import json
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
        Реалистичное движение мыши к заданной точке (x, y) через заранее рассчитанную траекторию.
        """
        current_x, current_y = pyautogui.position()
        template_width, _ = template_size

        # Рассчитываем промежуточные и финальные точки
        mid_target_x, mid_target_y = self._calculate_target(x, y, template_width, radius_range=(1.0, 2.5))
        final_target_x, final_target_y = self._calculate_target(x, y, template_width, radius_range=(0.1, 0.55))

        # Генерируем траектории
        mid_trajectory = self._calculate_bezier_trajectory(
            current_x, current_y, mid_target_x, mid_target_y, num_points=random.randint(3, 5)
        )
        final_trajectory = self._calculate_bezier_trajectory(
            mid_target_x, mid_target_y, final_target_x, final_target_y, num_points=random.randint(2, 3)
        )

        # Выполняем движение
        self._execute_trajectory(mid_trajectory, base_speed=self.config["base_speed"], acceleration="logarithmic")
        self._execute_trajectory(final_trajectory, base_speed=self.config["correction_speed"], acceleration="none")

    def _calculate_target(self, center_x, center_y, template_width, radius_range):
        """
        Рассчитывает целевую точку для движения в заданном радиусе от центра темплейта.
        :param radius_range: Кортеж с минимальным и максимальным радиусом (в процентах ширины темплейта).
        """
        radius_min = template_width * radius_range[0]  # Минимальный радиус
        radius_max = template_width * radius_range[1]  # Максимальный радиус

        while True:
            offset_x = random.uniform(-radius_max, radius_max)
            offset_y = random.uniform(-radius_max, radius_max)
            distance = math.sqrt(offset_x**2 + offset_y**2)

            if radius_min <= distance <= radius_max:
                return int(center_x + offset_x), int(center_y + offset_y)

    def _calculate_bezier_trajectory(self, start_x, start_y, end_x, end_y, num_points):
        """
        Вычисляет траекторию движения по кривой Безье.
        """
        control_points = [(start_x, start_y)]
        for _ in range(num_points - 2):
            control_x = random.randint(min(start_x, end_x), max(start_x, end_x))
            control_y = random.randint(min(start_y, end_y), max(start_y, end_y))
            control_points.append((control_x, control_y))
        control_points.append((end_x, end_y))

        return self._generate_bezier_curve(control_points)

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

    def _execute_trajectory(self, trajectory, base_speed, acceleration="linear", max_duration=1.0):
        """
        Выполняет движение по заданной траектории с постепенным увеличением скорости.
        Возвращает конечную скорость.
        """
        total_points = len(trajectory)
        previous_speed = base_speed  # Начальная скорость задается базовой

        for i, (x, y) in enumerate(trajectory):
            # Если это последний такт, устанавливаем быструю фиксированную скорость
            if i == total_points - 1:
                duration = 0.05  # Финальный такт выполняется очень быстро
            else:
                if i == 0:
                    # Для первой точки начинаем с базовой скорости
                    speed_factor = 1
                elif acceleration == "logarithmic":
                    progress = i / total_points
                    speed_factor = 1 + math.log(1 + progress * 10)
                else:
                    speed_factor = 1

                # Рассчитываем длительность текущего шага
                duration = (base_speed / total_points) / speed_factor

                # Учитываем предыдущую скорость
                if previous_speed > 0 and duration > 0:
                    previous_speed_factor = previous_speed / duration
                    duration /= max(previous_speed_factor, 1)  # Защита от деления на 0

                # Ограничиваем максимальную длительность
                duration = min(duration, max_duration / total_points)

            # Двигаем мышь
            pyautogui.moveTo(x, y, 0)

            # Обновляем предыдущую скорость
            previous_speed = 1 / duration if duration > 0 else base_speed

        return previous_speed  # Возвращаем конечную скорость

    def click(self):
        """
        Симулирует клик мыши.
        """
        pyautogui.click()
