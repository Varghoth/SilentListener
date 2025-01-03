from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QTableWidget, QPushButton, QLineEdit,
    QCheckBox, QFileDialog, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt
import logging


class AsyncSchedulerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(700, 300)  # Увеличиваем ширину окна

        # Логирование
        logging.info("Инициализация окна планировщика")

        # Основной виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Макет
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Таблица задач
        self.task_table = QTableWidget(0, 4)  # Колонки: Автозапуск, Запуск, Скрипт, Удаление
        self.task_table.setHorizontalHeaderLabels(["AS", "Start", "Script", "X"])
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

    def set_column_widths(self):
        """Устанавливает ширину столбцов в процентах от ширины окна."""
        column_widths = [3, 10, 83, 3]  # Процентное соотношение ширины столбцов
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
        run_button = QPushButton("Start")
        run_button.clicked.connect(lambda: self.run_task(row_count))
        self.task_table.setCellWidget(row_count, 1, run_button)

        # Выбор скрипта (текстовый ввод + выбор файла)
        script_widget = self.create_script_widget()
        self.task_table.setCellWidget(row_count, 2, script_widget)

        # Удаление строки (кнопка)
        delete_button = QPushButton("X")
        delete_button.setStyleSheet("color: black;")
        delete_button.clicked.connect(lambda: self.delete_task_row(row_count))
        self.task_table.setCellWidget(row_count, 3, delete_button)

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
        select_button = QPushButton("📂")
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

    def run_task(self, row):
        # Логика запуска скрипта
        script_widget = self.task_table.cellWidget(row, 2)
        if script_widget:
            script_input = script_widget.layout().itemAt(0).widget()
            script_path = script_input.text()

            if script_path:
                logging.info(f"Choose Script: {script_path}")
                # Здесь можно добавить вызов логики выполнения скрипта
            else:
                logging.warning(f"Скрипт не указан для строки {row + 1}")

    def delete_task_row(self, row):
        """Удаляет выбранную строку."""
        self.task_table.removeRow(row)
        logging.info(f"Строка {row + 1} удалена.")

    def load_tasks(self):
        """Логика загрузки задач."""
        logging.info("Загрузка задач...")
        # Здесь добавить логику загрузки задач из файла

    def save_tasks(self):
        """Логика сохранения задач."""
        logging.info("Сохранение задач...")
        # Здесь добавить логику сохранения задач в файл

    def start_all_tasks(self):
        """Запуск всех задач."""
        logging.info("Запуск всех задач...")
        # Здесь добавить логику для запуска всех задач

    def stop_all_tasks(self):
        """Остановка всех задач."""
        logging.info("Остановка всех задач...")
        # Здесь добавить логику для остановки всех задач

    def resizeEvent(self, event):
        """Обновляет ширину столбцов при изменении размера окна."""
        super().resizeEvent(event)
        self.set_column_widths()
