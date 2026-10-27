import sys
from pathlib import Path

from PyQt5.QtCore import QUrl, QObject, QTimer, pyqtSignal
from PyQt5.QtWidgets import QApplication
from PyQt5.QtQml import QQmlApplicationEngine


class Interface(QObject):
    saveRequested = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        # Путь к файлу для сохранения рисунка
        self.save_path = Path(__file__).resolve().parent / "canvas_autosave.png"

        # Таймер для автоматического сохранения каждые 5 секунд
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.save_canvas)
        self.timer.start(5000)

    def save_canvas(self):
        # Передаём QML сигнал на сохранение Canvas
        self.saveRequested.emit(self.save_path.as_posix())


if __name__ == '__main__':

    # Создаем экземпляр приложения
    app = QApplication(sys.argv)

    interface = Interface()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("_backend", interface)

    # Загружаем QML
    qml_path = Path(__file__).resolve().parent / "lab4" / "mainWindow.qml"
    engine.load(QUrl.fromLocalFile(str(qml_path)))

    # Проверка успешной загрузки QML
    if not engine.rootObjects():
        print("Ошибка: Не удалось загрузить QML файл!")
        sys.exit(-1)

    sys.exit(app.exec())
