import os
import cv2
import logging
from pathlib import Path

# Настройка логирования
logger = logging.getLogger("TemplateManager")
logging.basicConfig(level=logging.INFO)

# Получение корневого пути проекта
BASE_DIR = Path(__file__).resolve().parent

def get_full_path(relative_path):
    """Возвращает полный путь на основе корня проекта."""
    return os.path.join(BASE_DIR, relative_path)

def load_templates_from_folder(folder_path):
    """
    Загружает все файлы .png из указанной папки.
    :param folder_path: Путь к папке.
    :return: Словарь {имя файла: шаблон (numpy.ndarray)}.
    """
    logger.info(f"Загрузка шаблонов из папки: {folder_path}")
    if not os.path.exists(folder_path):
        logger.error(f"Папка не найдена: {folder_path}")
        return {}

    templates = {}
    invalid_files = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".png"):
            full_path = os.path.join(folder_path, file_name)
            template = cv2.imread(full_path, cv2.IMREAD_GRAYSCALE)
            if template is not None:
                templates[file_name] = template
            else:
                invalid_files.append(file_name)

    logger.info(f"Загружено {len(templates)} шаблонов из {folder_path}.")
    if invalid_files:
        logger.warning(f"Не удалось загрузить {len(invalid_files)} файлов: {invalid_files}")
    return templates

def load_all_templates(base_folder):
    """
    Рекурсивно загружает все шаблоны из базовой папки.
    :param base_folder: Путь к базовой папке.
    :return: Словарь шаблонов, сгруппированных по папкам.
    """
    logger.info(f"Начинаем загрузку шаблонов из {base_folder}")
    all_templates = {}
    for root, _, _ in os.walk(base_folder):
        category = os.path.relpath(root, base_folder)  # Категория = относительный путь
        templates = load_templates_from_folder(root)
        if templates:
            all_templates[category] = templates
    logger.info(f"Шаблоны успешно загружены. Категорий: {len(all_templates)}")
    return all_templates

def get_template(category, name):
    """
    Возвращает шаблон по категории и имени.
    :param category: Категория шаблона.
    :param name: Имя файла шаблона (с расширением .png).
    :return: Шаблон (numpy.ndarray) или None.
    """
    category_templates = TEMPLATES.get(category, {})
    template = category_templates.get(name)
    if template is None:
        logger.warning(f"Шаблон {name} в категории {category} не найден.")
    return template

# Базовая папка для шаблонов
TEMPLATE_BASE_FOLDER = get_full_path("templates")
TEMPLATES = load_all_templates(TEMPLATE_BASE_FOLDER)

# Пример использования
if __name__ == "__main__":
    # Пример: получение шаблона из категории "play"
    template = get_template("play", "play_button.png")
    if template is not None:
        logger.info("Шаблон успешно получен и готов к использованию!")
    else:
        logger.error("Шаблон не найден.")