import os
import json
import random
import time
from global_storage import load_templates_from_folder  # Используем существующую функцию

CONFIG_FILE = "/app/DCA_config/autoplaylist_config.json"
WHITE_LIST_FILE = "/app/DCA_config/white_list.json"


def load_or_create_config():
    """Загружает или создаёт файл конфигурации для автосбора плейлистов."""
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "min_tracks": 30,
            "current_tracks": 0,
            "balance_ratio": 0.5  # Соотношение наших/сторонних
        }
        with open(CONFIG_FILE, "w") as file:
            json.dump(default_config, file, indent=4)
        print(f"Создан конфигурационный файл: {CONFIG_FILE}")
        return default_config
    else:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)


def parse_playlist(playlist_name):
    """Симулирует парсинг плейлиста 'Любимое'."""
    print(f"Парсим плейлист: {playlist_name}")
    # Подключаем машинное зрение или используем мок-данные для тестов
    tracks = {"our": 10, "others": 20, "total": 30}  # Пример результата
    return tracks


def play_random_album():
    """Выбирает случайный альбом из белого списка и эмулирует его воспроизведение."""
    with open(WHITE_LIST_FILE, "r") as file:
        white_list = json.load(file)
    album = random.choice(white_list)
    print(f"Проигрываем альбом: {album}")
    # Здесь будет логика прокрутки и автоклика для старта альбома


def like_tracks_periodically(interval=300):
    """Ставит лайки трекам через заданный интервал."""
    print(f"Ставим лайки каждые {interval} секунд")
    # Логика автоклика лайков
    time.sleep(interval)


def balance_playlist():
    """Анализирует и балансирует треки в плейлисте."""
    config = load_or_create_config()
    parsed_tracks = parse_playlist("Любимое")
    current_ratio = parsed_tracks["our"] / max(parsed_tracks["total"], 1)

    if current_ratio < config["balance_ratio"]:
        print("Недостаточно наших треков, корректируем...")
        play_random_album()
    else:
        print("Баланс треков в норме.")
