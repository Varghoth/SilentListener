import random
import time

class StreamingSimulator:
    def __init__(self):
        self.status = "playing"  # Возможные статусы: "playing", "paused"

    def check_streaming_status(self):
        """
        Проверяет статус воспроизведения.
        """
        # Здесь можно добавить реальную логику проверки статуса (например, через скриншот или API)
        return self.status

    def set_streaming_status(self, status):
        """
        Устанавливает статус воспроизведения.
        """
        self.status = status
        print(f"Статус изменен на: {status}")

    def random_action(self):
        """
        Выбирает случайное действие на основе заданных вероятностей.
        """
        actions = {
            "idle": 85,
            "play": 5,
            "pause": 5,
            "next": 3,
            "previous": 2,
        }
        total = sum(actions.values())
        rand = random.uniform(0, total)
        cumulative = 0
        for action, weight in actions.items():
            cumulative += weight
            if rand <= cumulative:
                return action

    def perform_action(self, action):
        """
        Выполняет действие в зависимости от выбранного.
        """
        if action == "idle":
            print("Ничего не делаем (idle).")
        elif action == "play":
            if self.check_streaming_status() == "paused":
                self.set_streaming_status("playing")
                print("Воспроизведение запущено (play).")
            else:
                print("Музыка уже воспроизводится.")
        elif action == "pause":
            if self.check_streaming_status() == "playing":
                self.set_streaming_status("paused")
                print("Музыка поставлена на паузу (pause).")
            else:
                print("Музыка уже на паузе.")
        elif action == "next":
            print("Переключаем на следующий трек (next).")
        elif action == "previous":
            print("Переключаем на предыдущий трек (previous).")

    def run_simulation(self):
        """
        Основной цикл симуляции.
        """
        while True:
            # Проверяем статус воспроизведения
            current_status = self.check_streaming_status()
            if current_status == "paused":
                print("Музыка на паузе. Запускаем воспроизведение.")
                self.set_streaming_status("playing")

            # Выбираем случайное действие
            action = self.random_action()
            print(f"Выбрано действие: {action}")

            # Выполняем действие
            self.perform_action(action)

            # Ждем перед следующим циклом
            delay = random.uniform(300, 360)  # 5-6 минут (для релиза: 15-30 минут)
            print(f"Ожидание {delay:.2f} секунд перед следующим действием.")
            time.sleep(delay)
