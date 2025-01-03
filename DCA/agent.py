from PyQt5.QtWidgets import QApplication
from async_scheduler_window import AsyncSchedulerWindow
import sys

def main():
    # Создаём приложение
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    # Создаём основное окно — планировщик
    scheduler_window = AsyncSchedulerWindow()
    scheduler_window.setWindowTitle("DCA Scheduler")
    scheduler_window.show()

    # Запускаем главный цикл
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
