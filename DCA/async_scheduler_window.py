from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QTableWidget, QPushButton, QLineEdit,
    QCheckBox, QFileDialog, QTableWidgetItem, QHeaderView, QDialog, QTextEdit, QApplication
)
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QPalette, QColor, QIcon, QRegExpValidator  # Добавляем правильный импорт QPalette и QColor

from modules.script_actions import ScriptActions
from modules.task_manager import TaskManager

from qasync import QEventLoop
import asyncio
import logging
import json
import sys
import os

class LogWindow(QDialog):
    """Окно для отображения логов."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Logs")
        self.resize(700, 400)

        # Основное текстовое поле для логов
        self.log_text = QTextEdit(self)
        self.log_text.setReadOnly(True)

        # Кнопка очистки логов
        clear_button = QPushButton("Clear Logs")
        clear_button.clicked.connect(self.clear_logs)

        # Макет окна
        layout = QVBoxLayout()
        layout.addWidget(self.log_text)
        layout.addWidget(clear_button)
        self.setLayout(layout)

    def append_log(self, message):
        """Добавляет строку в текстовое поле."""
        self.log_text.append(message)

    def clear_logs(self):
        """Очищает текстовое поле."""
        self.log_text.clear()

class LogHandler(logging.Handler):
    """Кастомный логгер для перенаправления сообщений в окно."""
    def __init__(self, log_window):
        super().__init__()
        self.log_window = log_window

    def emit(self, record):
        message = self.format(record)
        self.log_window.append_log(message)

class AsyncSchedulerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Инициализируем QEventLoop для qasync
        self.loop = asyncio.get_event_loop()

        self.dca_root = os.path.join(os.path.dirname(__file__), "..", "DCA") # Определяем корневой каталог DCA
        self.script_actions = ScriptActions(self.loop)  # Создаем экземпляр ScriptActions один раз
        self.resize(700, 300)  # Увеличиваем ширину окна
        self.apply_dark_theme()  # Применяем темную тему
        self.task_manager = TaskManager(loop=self.loop)  # Подключаем TaskManager

        # Устанавливаем путь к иконке
        icon_path = os.path.join(self.dca_root, "assets", "icon.png")
        self.setWindowIcon(QIcon(icon_path))  # Устанавливаем пользовательскую иконку

        # Флаг отображения окна логов
        self.show_logs = False

        # Инициализация логов
        self.log_window = LogWindow()
        self.setup_logging()

        # Логирование
        logging.info("Инициализация окна планировщика")

        # Основной виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Таблица задач
        self.task_table = QTableWidget(0, 6)  # Колонки: Автозапуск, Запуск, Скрипт, Удаление
        self.task_table.setHorizontalHeaderLabels(["⚙", "▷", "Script", "☀︎", "☾", "✖"])
        self.task_table.horizontalHeader().setStretchLastSection(False)
        self.task_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  # Показываем вертикальную прокрутку всегда
        layout.addWidget(self.task_table)

        # Устанавливаем ширину столбцов в процентах
        self.set_column_widths()

        # Контейнер для кнопок
        button_layout = QHBoxLayout()

        # Кнопка добавления задачи
        add_task_button = QPushButton("Add Task")
        add_task_button.clicked.connect(self.add_task_row)
        button_layout.addWidget(add_task_button)

        # Кнопка загрузки
        load_button = QPushButton("Load")
        load_button.clicked.connect(self.load_tasks)
        button_layout.addWidget(load_button)

        # Кнопка сохранения
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_tasks)
        button_layout.addWidget(save_button)

        # Кнопка запуска всех задач
        start_all_button = QPushButton("Start All")
        start_all_button.clicked.connect(self.start_all_tasks)
        button_layout.addWidget(start_all_button)

        # Кнопка остановки всех задач
        stop_all_button = QPushButton("Stop All")
        stop_all_button.clicked.connect(self.stop_all_tasks)
        button_layout.addWidget(stop_all_button)

        # Добавляем контейнер с кнопками
        layout.addLayout(button_layout)

        # Загружаем задачи из файла при запуске
        self.load_tasks()

        # Запуск автозапускаемых задач
        self.run_autostart_tasks()

        # Показываем окно логов, если включен флаг
        if self.show_logs:
            self.log_window.show()

############################### [START] Окно Планировщика ###############################

    def set_column_widths(self):
        """Устанавливает ширину столбцов в процентах от ширины окна."""
        column_widths = [3, 4, 72, 9, 9, 2]  # Процентное соотношение ширины столбцов
        total_width = self.task_table.viewport().width()

        for i, percentage in enumerate(column_widths):
            self.task_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Fixed)
            self.task_table.setColumnWidth(i, int(total_width * percentage / 100))

    def add_task_row(self):
        row_count = self.task_table.rowCount()
        self.task_table.insertRow(row_count)

        # Автозапуск (галочка)
        auto_start_checkbox = QCheckBox()
        auto_start_checkbox.setChecked(False)
        self.task_table.setCellWidget(row_count, 0, auto_start_checkbox)

        # Запуск скрипта (кнопка)
        run_button_container = QWidget()
        run_button_layout = QHBoxLayout()
        run_button_layout.setContentsMargins(0, 0, 0, 0)
        run_button = QPushButton("▷")
        run_button.clicked.connect(lambda: self.loop.create_task(self.run_task(row_count)))  # Используем QEventLoop
        run_button_layout.addWidget(run_button)
        run_button_container.setLayout(run_button_layout)
        self.task_table.setCellWidget(row_count, 1, run_button_container)

        # Выбор скрипта (текстовый ввод + выбор файла)
        script_widget = self.create_script_widget()
        self.task_table.setCellWidget(row_count, 2, script_widget)

        # Время начала выполнения
        start_time_input = QLineEdit()
        start_time_input.setPlaceholderText("HH:MM")
        start_time_input.setValidator(QRegExpValidator(QRegExp(r"^([01]?\d|2[0-3]):[0-5]\d$")))  # Валидация времени
        start_time_input.textChanged.connect(self.validate_time_intervals)  # Проверяем пересечения
        self.task_table.setCellWidget(row_count, 3, start_time_input)

        # Время окончания выполнения
        end_time_input = QLineEdit()
        end_time_input.setPlaceholderText("HH:MM")
        end_time_input.setValidator(QRegExpValidator(QRegExp(r"^([01]?\d|2[0-3]):[0-5]\d$")))  # Валидация времени
        end_time_input.textChanged.connect(self.validate_time_intervals)  # Проверяем пересечения
        self.task_table.setCellWidget(row_count, 4, end_time_input)

        # Удаление строки (кнопка)
        delete_button = QPushButton("✖")
        delete_button.clicked.connect(lambda: self.delete_task_row(row_count))
        self.task_table.setCellWidget(row_count, 5, delete_button)

        logging.info(f"[UI] Добавлена задача в строку {row_count}")

    def create_script_widget(self):
        # Создаем контейнер для текстового ввода и кнопки выбора файла
        container = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Поле для ввода текста
        script_input = QLineEdit()
        script_input.setPlaceholderText("Choose Script...")
        layout.addWidget(script_input)

        # Кнопка выбора файла
        select_button = QPushButton("...")
        select_button.setFixedSize(30, 30)
        select_button.clicked.connect(lambda: self.select_script_file(script_input))
        layout.addWidget(select_button)

        container.setLayout(layout)
        return container

    def select_script_file(self, line_edit):
        # Открываем диалог выбора файла
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choose Script", "", "Python Scripts (*.json);;All Files (*)"
        )
        if file_path:
            line_edit.setText(file_path)

    def delete_task_row(self, row):
        """Удаляет выбранную строку."""
        self.task_table.removeRow(row)
        logging.info(f"Строка {row + 1} удалена.")

    def setup_logging(self):
        """Настраивает логирование для приложения."""
        log_handler = LogHandler(self.log_window)
        log_handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        log_handler.setFormatter(formatter)

        logging.getLogger().addHandler(log_handler)
        logging.getLogger().setLevel(logging.INFO)

    def resizeEvent(self, event):
        """Обновляет ширину столбцов при изменении размера окна."""
        super().resizeEvent(event)
        self.set_column_widths()

    def apply_dark_theme(self):
        dark_palette = QPalette()

        # Настройка цветов
        dark_palette.setColor(QPalette.Window, QColor(64, 69, 82))
        dark_palette.setColor(QPalette.WindowText, QColor(160, 166, 178))  # Белый
        dark_palette.setColor(QPalette.Base, QColor(64, 69, 82))
        dark_palette.setColor(QPalette.AlternateBase, QColor(64, 69, 82))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(160, 166, 178))  # Белый
        dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Text, QColor(160, 166, 178))  # Белый
        dark_palette.setColor(QPalette.Button, QColor(47, 52, 63))
        dark_palette.setColor(QPalette.ButtonText, QColor(160, 166, 178))  # Белый
        dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        dark_palette.setColor(QPalette.Highlight, QColor(160, 166, 178))  # Белый
        dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))

        # Применяем палитру
        self.setPalette(dark_palette)

        # Стилизация через CSS
        self.setStyleSheet("""
            QMainWindow {
                background-color: rgb(64, 69, 82);
            }
            QLabel, QTableWidget, QHeaderView::section {
                color: rgb(160, 166, 178);  /* Белый */
            }
            QPushButton {
                background-color: rgb(47, 52, 63);
                color: rgb(175, 184, 198);  /* Медово-золотой */
                border: 1px solid rgb(175, 184, 198);  /* Золотая рамка */
            }
            QPushButton:hover {
                background-color: rgb(175, 184, 198);
                color: rgb(0, 0, 0);  /* Чёрный текст */
            }
            QLineEdit, QTimeEdit {
                background-color: rgb(25, 25, 25);
                color: rgb(160, 166, 178);  /* Белый */
                border: 1px solid rgb(47, 52, 63);
            }
            QTableWidget {
                background-color: rgb(25, 25, 25);
                color: rgb(160, 166, 178);  /* Белый */
                gridline-color: rgb(47, 52, 63);
            }
            QWidget {
                background-color: rgb(47, 52, 63);
            }
            QCheckBox {
                color: rgb(160, 166, 178);  /* Белый */
                spacing: 5px; /* Расстояние между флажком и текстом */
            }
            QCheckBox::indicator {
                width: 18px; /* Ширина флажка */
                height: 18px; /* Высота флажка */
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid rgb(175, 184, 198); /* Золотая рамка */
                background-color: rgb(47, 52, 63); /* Тёмный фон */
            }
            QCheckBox::indicator:checked {
                border: 2px solid rgb(175, 184, 198); /* Золотая рамка */
                background-color: rgb(175, 184, 198); /* Золотой фон */
            }
            QLabel, QLineEdit {
                color: rgb(175, 184, 198); /* Медово-золотой текст */
                background-color: rgb(47, 52, 63); /* Тёмный фон */
            }
            QComboBox {
                color: rgb(175, 184, 198);
                background-color: rgb(47, 52, 63);
            }
            QListView, QTreeView {
                color: rgb(175, 184, 198);
                background-color: rgb(47, 52, 63);
            }
            QPushButton {
                color: rgb(175, 184, 198);
                background-color: rgb(47, 52, 63);
                border: 1px solid rgb(175, 184, 198);
            }
            QPushButton:hover {
                background-color: rgb(175, 184, 198);
                color: rgb(0, 0, 0);
            }
            QHeaderView::section {
                background-color: rgb(47, 52, 63);
                color: rgb(175, 184, 198);
            }
            QScrollBar {
                background-color: rgb(47, 52, 63);
            }
        """)

    def validate_time_intervals(self):
        tasks = []
        for row in range(self.task_table.rowCount()):
            start_widget = self.task_table.cellWidget(row, 3)
            end_widget = self.task_table.cellWidget(row, 4)
            if start_widget and end_widget:
                start_time = start_widget.text()
                end_time = end_widget.text()

                if start_time and end_time:
                    tasks.append((start_time, end_time, row))

        # Проверяем пересечения времени
        tasks.sort(key=lambda x: x[0])  # Сортируем по времени начала
        for i in range(len(tasks) - 1):
            _, end_time, current_row = tasks[i]
            next_start_time, _, next_row = tasks[i + 1]

            if end_time > next_start_time:  # Если время пересекается
                self.task_table.cellWidget(next_row, 3).setStyleSheet("border: 2px solid red;")
            else:
                self.task_table.cellWidget(next_row, 3).setStyleSheet("")

############################### [-END-] Окно Планировщика ###############################

############################### [START] Задачи ###############################

    def load_tasks(self):
        """Загружает задачи из файла tasks.json, если он существует, и заменяет текущие задачи."""
        tasks_file_path = os.path.join(self.dca_root, "tasks.json")

        if not os.path.exists(tasks_file_path):
            logging.info(f"Файл {tasks_file_path} не найден. Пропускаем загрузку задач.")
            return

        try:
            with open(tasks_file_path, "r", encoding="utf-8") as file:
                tasks = json.load(file)
                logging.info(f"Задачи успешно загружены из {tasks_file_path}")
        except Exception as e:
            logging.error(f"Ошибка при загрузке задач из {tasks_file_path}: {e}")
            return

        # Очищаем таблицу перед загрузкой новых данных
        self.task_table.setRowCount(0)

        # Заполняем таблицу задач
        for task in tasks:
            self.add_task_row()
            row_count = self.task_table.rowCount() - 1

            # Устанавливаем состояние автозапуска
            auto_start_checkbox = self.task_table.cellWidget(row_count, 0)
            if auto_start_checkbox and "auto_start" in task:
                auto_start_checkbox.setChecked(task["auto_start"])

            # Устанавливаем путь к скрипту
            script_widget = self.task_table.cellWidget(row_count, 2)
            if script_widget and "script_path" in task:
                script_input = script_widget.layout().itemAt(0).widget()
                if script_input:
                    script_input.setText(task["script_path"])

            # Устанавливаем время начала выполнения
            start_time_input = self.task_table.cellWidget(row_count, 3)
            if start_time_input and "start_time" in task:
                start_time_input.setText(task["start_time"])

            # Устанавливаем время окончания выполнения
            end_time_input = self.task_table.cellWidget(row_count, 4)
            if end_time_input and "end_time" in task:
                end_time_input.setText(task["end_time"])

    def save_tasks(self):
        """Сохраняет текущую конфигурацию задач в файл JSON в каталоге DCA."""
        tasks = []

        for row in range(self.task_table.rowCount()):
            # Извлечение данных из столбцов
            auto_start_checkbox = self.task_table.cellWidget(row, 0)
            run_button = self.task_table.cellWidget(row, 1)
            script_widget = self.task_table.cellWidget(row, 2)
            start_time_input = self.task_table.cellWidget(row, 3)
            end_time_input = self.task_table.cellWidget(row, 4)

            # Получаем состояние автозапуска
            auto_start = auto_start_checkbox.isChecked() if auto_start_checkbox else False

            # Получаем путь к скрипту
            script_input = script_widget.layout().itemAt(0).widget() if script_widget else None
            script_path = script_input.text() if script_input else ""

            # Получаем время начала и окончания выполнения
            start_time = start_time_input.text() if start_time_input else ""
            end_time = end_time_input.text() if end_time_input else ""

            # Добавляем задачу в список
            tasks.append({
                "auto_start": auto_start,
                "script_path": script_path,
                "start_time": start_time,
                "end_time": end_time
            })

        # Путь к файлу tasks.json в каталоге DCA
        tasks_file_path = os.path.join(self.dca_root, "tasks.json")

        # Сохраняем список задач в файл JSON
        try:
            with open(tasks_file_path, "w", encoding="utf-8") as file:
                json.dump(tasks, file, indent=4, ensure_ascii=False)
            logging.info(f"Конфигурация успешно сохранена в {tasks_file_path}")
        except Exception as e:
            logging.error(f"Ошибка при сохранении задач в {tasks_file_path}: {e}")

    def run_autostart_tasks(self):
        """Запускает все задачи, отмеченные для автозапуска."""
        for row in range(self.task_table.rowCount()):
            auto_start_checkbox = self.task_table.cellWidget(row, 0)
            if auto_start_checkbox and auto_start_checkbox.isChecked():
                logging.info(f"[UI] Автозапуск задачи в строке {row}")
                self.loop.create_task(self.run_task(row))  # Используем асинхронный запуск задачи


    async def run_task(self, row):
        try:
            run_button = self._get_widget_from_row(row, column=1, widget_type=QPushButton)
            script_input = self._get_widget_from_row(row, column=2, widget_type=QLineEdit)
            script_path = script_input.text() if script_input else None

            if not script_path:
                logging.warning(f"[UI] Скрипт не указан для строки {row + 1}")
                return

            if run_button.text() == "▷":
                run_button.setText("☐")
                logging.info(f"[UI] Задача {row + 1}: Запуск скрипта {script_path}")
                await self.task_manager.start_task(script_path)
            else:
                run_button.setText("▷")
                logging.info(f"[UI] Задача {row + 1}: Остановка скрипта {script_path}")
                self.task_manager.stop_task(script_path)

        except Exception as e:
            logging.error(f"[UI] Ошибка при запуске задачи: {e}")

    def _get_widget_from_row(self, row, column, widget_type):
        """Получает виджет заданного типа из указанной строки и столбца таблицы.

        :param row: Номер строки.
        :param column: Номер столбца.
        :param widget_type: Ожидаемый тип виджета (например, QPushButton, QLineEdit).
        :return: Найденный виджет или None, если виджет отсутствует.
        """
        try:
            widget_container = self.task_table.cellWidget(row, column)
            if not widget_container:
                logging.error(f"[UI] Контейнер виджета отсутствует в строке {row}, колонке {column}")
                return None

            if isinstance(widget_container, QWidget):
                layout = widget_container.layout()
                if layout and layout.count() > 0:
                    widget = layout.itemAt(0).widget()
                    if isinstance(widget, widget_type):
                        return widget

            elif isinstance(widget_container, widget_type):
                return widget_container

            logging.error(f"[UI] Виджет типа {widget_type.__name__} отсутствует в строке {row}, колонке {column}")
            return None

        except Exception as e:
            logging.error(f"[UI] Ошибка при извлечении виджета из строки {row}, колонки {column}: {e}")
            return None

    async def start_task(self, script_path):
        if script_path in self.tasks:
            logging.warning(f"[TaskManager] Задача уже выполняется: {script_path}")
            return

        cancel_event = asyncio.Event()
        task = self.loop.create_task(self.execute_task(script_path, cancel_event))
        self.tasks[script_path] = (task, cancel_event)
        logging.info(f"[TaskManager] Задача запущена: {script_path}")

    def stop_task(self, script_path):
        self.task_manager.stop_task(script_path)
        logging.info(f"[UI] Задача {script_path} остановлена")

    def start_all_tasks(self):
        """Запуск всех задач."""
        logging.info("Запуск всех задач...")
        for row in range(self.task_table.rowCount()):
            script_path = self.get_script_path(row)
            if script_path:
                self.start_task(script_path)

    def stop_all_tasks(self):
        """Остановка всех задач."""
        logging.info("Остановка всех задач...")
        # Здесь добавить логику для остановки всех задач

############################### [-END-] Задачи ###############################