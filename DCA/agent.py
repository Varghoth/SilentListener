from PyQt5.QtWidgets import QApplication
from async_scheduler_window import AsyncSchedulerWindow
from qasync import QEventLoop
import asyncio
import sys

def main():
    # Создаём приложение
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # Создаём основное окно — планировщик
    scheduler_window = AsyncSchedulerWindow()
    scheduler_window.setWindowTitle("DCA Scheduler")
    scheduler_window.show()

    # Запускаем главный цикл событий
    with loop:
        sys.exit(loop.run_forever())

if __name__ == "__main__":
    main()
