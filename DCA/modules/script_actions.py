import subprocess
import logging
import asyncio


class ScriptActions:
    """
    Класс для управления действиями, вызываемыми из скриптов.
    """

    def __init__(self):
        """
        Инициализация класса ScriptActions.
        """
        self.actions = {
            "check_firefox": self.check_firefox_action,
            "log_message": self.log_message_action,
            "wait": self.wait_action,
        }

    async def check_firefox_action(self, params=None):
        """
        Проверяет, запущен ли Firefox, и запускает его, если не запущен.
        :param params: Параметры действия (опционально, для совместимости с другими действиями).
        """
        try:
            logging.info("[CHECK_FIREFOX_ACTION] Проверяем, запущен ли Firefox...")
            result = subprocess.run(
                ["pgrep", "-x", "firefox"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if result.returncode == 0:
                logging.info("[CHECK_FIREFOX_ACTION] Firefox уже запущен.")
            else:
                logging.info("[CHECK_FIREFOX_ACTION] Firefox не запущен. Запускаем...")
                subprocess.Popen(["firefox"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                await asyncio.sleep(2)  # Небольшая задержка для запуска
                logging.info("[CHECK_FIREFOX_ACTION] Firefox успешно запущен.")
        except Exception as e:
            logging.error(f"[CHECK_FIREFOX_ACTION] Ошибка: {e}")

    async def log_message_action(self, params):
        """
        Логирует сообщение из переданных параметров.
        :param params: {"message": "Ваше сообщение"}
        """
        try:
            message = params.get("message", "Нет сообщения")
            logging.info(f"[LOG_MESSAGE_ACTION] {message}")
        except Exception as e:
            logging.error(f"[LOG_MESSAGE_ACTION] Ошибка: {e}")

    async def wait_action(self, params):
        """
        Выполняет задержку на указанное количество секунд.
        :param params: {"duration": 5}
        """
        try:
            duration = params.get("duration", 0)
            logging.info(f"[WAIT_ACTION] Задержка {duration} секунд.")
            await asyncio.sleep(duration)
            logging.info("[WAIT_ACTION] Задержка завершена.")
        except Exception as e:
            logging.error(f"[WAIT_ACTION] Ошибка: {e}")

    def get_action(self, action_name):
        """
        Возвращает действие по его имени.
        :param action_name: Имя действия.
        :return: Функция действия или None, если действие не найдено.
        """
        return self.actions.get(action_name)


# Настройка логирования
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")

# Пример использования
if __name__ == "__main__":
    actions = ScriptActions()

    # Пример вызова действий
    asyncio.run(actions.check_firefox_action())
    asyncio.run(actions.log_message_action({"message": "Привет, мир!"}))
    asyncio.run(actions.wait_action({"duration": 2}))
