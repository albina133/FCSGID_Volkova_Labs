import sqlite3
import sys
from pathlib import Path

from PyQt6 import uic
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QApplication, QFileDialog, QInputDialog, QMainWindow, QMessageBox


PROJECT_DIR = Path(__file__).resolve().parent
DEMO_DB = PROJECT_DIR / "lab3.db"


def create_demo_database():
    """Создаёт учебную БД, если её ещё нет."""
    with sqlite3.connect(DEMO_DB) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY,
                full_name TEXT NOT NULL,
                group_name TEXT NOT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY,
                student_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                grade INTEGER NOT NULL
            )
        """)
        if db.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 0:
            db.executemany(
                "INSERT INTO students (full_name, group_name) VALUES (?, ?)",
                [
                    ("Анна Иванова", "6233"),
                    ("Мария Петрова", "6233"),
                    ("Елена Смирнова", "6234"),
                ],
            )
        if db.execute("SELECT COUNT(*) FROM grades").fetchone()[0] == 0:
            db.executemany(
                "INSERT INTO grades (student_id, subject, grade) VALUES (?, ?, ?)",
                [
                    (1, "Базы данных", 5),
                    (2, "Базы данных", 4),
                    (3, "Программирование", 5),
                ],
            )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(str(PROJECT_DIR / "form.ui"), self)

        self.db = None
        self.tables = [self.table1, self.table2, self.table3, self.table4, self.table5]
        self.user_tables = []

        self.actionSetConnection.triggered.connect(self.set_connection)
        self.actionCloseConnection.triggered.connect(self.close_connection)
        self.actionCustomQuery.triggered.connect(self.custom_query)
        self.btn1.clicked.connect(self.query_btn1)
        self.btn2.clicked.connect(self.query_btn2)
        self.btn3.clicked.connect(self.query_btn3)
        self.comboColumns.currentTextChanged.connect(self.query_column)

        self.clear_tables()
        self.set_connected(False)
        self.statusbar.showMessage("База данных не подключена")

    def set_connected(self, connected):
        for control in (self.btn1, self.btn2, self.btn3, self.comboColumns,
                        self.actionCloseConnection, self.actionCustomQuery):
            control.setEnabled(connected)

    def clear_tables(self):
        for table in self.tables:
            table.setModel(QStandardItemModel(table))
            table.setAlternatingRowColors(True)
            table.horizontalHeader().setStretchLastSection(True)
        self.comboColumns.blockSignals(True)
        self.comboColumns.clear()
        self.comboColumns.blockSignals(False)
        self.tabWidget.setCurrentIndex(0)

    def set_connection(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Выберите базу данных SQLite", str(PROJECT_DIR),
            "SQLite (*.db *.sqlite *.sqlite3);;Все файлы (*)"
        )
        if not filename:
            return

        connection = None
        try:
            connection = sqlite3.connect(filename)
            connection.execute("SELECT * FROM sqlite_master").fetchall()
            user_tables = [row[0] for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' "
                "AND name NOT LIKE 'sqlite_%' ORDER BY rowid"
            )]
        except sqlite3.Error as error:
            if connection is not None:
                connection.close()
            QMessageBox.critical(self, "Ошибка подключения", str(error))
            return

        self.close_connection()
        self.db = connection
        self.user_tables = user_tables
        self.set_connected(True)
        self.comboColumns.blockSignals(True)
        self.comboColumns.addItems(["type", "name", "tbl_name", "rootpage", "sql"])
        self.comboColumns.setCurrentIndex(-1)
        self.comboColumns.blockSignals(False)
        self.run_query("SELECT * FROM sqlite_master", 0)
        self.statusbar.showMessage(f"Подключено: {filename}")

    def close_connection(self):
        if self.db is not None:
            self.db.close()
            self.db = None
        self.user_tables = []
        self.clear_tables()
        self.set_connected(False)
        self.statusbar.showMessage("База данных не подключена")

    def run_query(self, query, tab_index):
        if self.db is None:
            return
        try:
            cursor = self.db.execute(query)
            headers = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
        except sqlite3.Error as error:
            QMessageBox.warning(self, "Ошибка SQL", str(error))
            return

        model = QStandardItemModel(self)
        model.setHorizontalHeaderLabels(headers)
        for row in rows:
            model.appendRow([
                QStandardItem("NULL" if value is None else str(value))
                for value in row
            ])
        self.tables[tab_index].setModel(model)
        self.tabWidget.setCurrentIndex(tab_index)
        self.statusbar.showMessage(f"Запрос выполнен: {len(rows)} строк")

    def query_btn1(self):
        self.run_query("SELECT name FROM sqlite_master", 1)

    def query_column(self, column):
        if column:
            safe_column = column.replace('"', '""')
            self.run_query(f'SELECT "{safe_column}" FROM sqlite_master', 2)

    @staticmethod
    def quote_name(name):
        return '"' + name.replace('"', '""') + '"'

    def query_btn2(self):
        if not self.user_tables:
            QMessageBox.information(self, "Нет таблиц", "В базе нет пользовательских таблиц.")
            return
        self.run_query(f"SELECT * FROM {self.quote_name(self.user_tables[0])}", 3)

    def query_btn3(self):
        if not self.user_tables:
            QMessageBox.information(self, "Нет таблиц", "В базе нет пользовательских таблиц.")
            return
        if len(self.user_tables) >= 2:
            query = f"SELECT * FROM {self.quote_name(self.user_tables[1])}"
        else:
            query = f"SELECT COUNT(*) AS total_rows FROM {self.quote_name(self.user_tables[0])}"
        self.run_query(query, 4)

    def custom_query(self):
        query, accepted = QInputDialog.getMultiLineText(
            self, "SQL-запрос", "Введите SELECT-запрос:",
            "SELECT * FROM sqlite_master"
        )
        if not accepted or not query.strip():
            return
        if query.split()[0].upper() != "SELECT":
            QMessageBox.warning(self, "Недопустимый запрос", "Разрешены только SELECT-запросы.")
            return
        self.run_query(query, 4)

    def closeEvent(self, event):
        if self.db is not None:
            self.db.close()
        event.accept()


if __name__ == "__main__":
    create_demo_database()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
