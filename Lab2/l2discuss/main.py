import sys

from PyQt5.QtCore import (
    Qt,
    QRectF,
    QPropertyAnimation,
    QEasingCurve,
    pyqtProperty
)

from PyQt5.QtGui import (
    QColor,
    QPainter,
    QPen,
    QBrush,
    QLinearGradient
)

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QDoubleSpinBox,
    QLabel,
    QPushButton,
    QFrame,
    QVBoxLayout,
    QHBoxLayout
)

from l2discuss import cl1
from l2discuss import cl2


class ThermometerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._display_temperature = 20.0
        self.animation = QPropertyAnimation(self, b"displayTemperature")
        self.animation.setDuration(350)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)

        self.setFixedSize(300, 450)

    def getDisplayTemperature(self):
        return self._display_temperature

    def setDisplayTemperature(self, value):
        self._display_temperature = value
        self.update()

    displayTemperature = pyqtProperty(
        float,
        fget=getDisplayTemperature,
        fset=setDisplayTemperature
    )

    def setTemperature(self, value):
        value = max(-50.0, min(100.0, value))
        self.animation.stop()
        self.animation.setStartValue(self._display_temperature)
        self.animation.setEndValue(value)
        self.animation.start()

    def blendColors(self, c1, c2, t):
        t = max(0.0, min(1.0, t))
        r = int(c1.red() + (c2.red() - c1.red()) * t)
        g = int(c1.green() + (c2.green() - c1.green()) * t)
        b = int(c1.blue() + (c2.blue() - c1.blue()) * t)
        return QColor(r, g, b)

    def getColorForTemperature(self, temperature):

        if temperature <= 0:
            t = (temperature + 50.0) / 50.0
            return self.blendColors(
                QColor(80, 170, 255),
                QColor(140, 220, 255),
                t
            )
        elif temperature <= 25:
            t = temperature / 25.0
            return self.blendColors(
                QColor(140, 220, 255),
                QColor(255, 221, 120),
                t
            )
        elif temperature <= 50:
            t = (temperature - 25.0) / 25.0
            return self.blendColors(
                QColor(255, 221, 120),
                QColor(255, 170, 70),
                t
            )
        else:
            t = (temperature - 50.0) / 50.0
            return self.blendColors(
                QColor(255, 170, 70),
                QColor(255, 95, 85),
                t
            )

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        painter.fillRect(rect, Qt.transparent)

        center_x = rect.width() * 0.42
        bulb_radius = 42
        tube_width = 36
        tube_height = 300
        tube_top = 50
        bulb_center_y = tube_top + tube_height + bulb_radius - 4

        tube_rect = QRectF(
            center_x - tube_width / 2,
            tube_top,
            tube_width,
            tube_height
        )

        outer_tube_rect = QRectF(
            center_x - 26,
            tube_top - 18,
            52,
            tube_height + 36
        )

        painter.setPen(QPen(QColor("#5d6e9e"), 2))
        painter.setBrush(QBrush(QColor("#1a2341")))
        painter.drawRoundedRect(outer_tube_rect, 24, 24)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor("#0d1630")))
        painter.drawRoundedRect(tube_rect, 14, 14)

        temperature = max(-50.0, min(100.0, self._display_temperature))
        ratio = (temperature + 50.0) / 150.0

        fill_height = tube_height * ratio
        fill_rect = QRectF(
            tube_rect.left(),
            tube_rect.bottom() - fill_height,
            tube_rect.width(),
            fill_height
        )

        fluid_color = self.getColorForTemperature(temperature)

        gradient = QLinearGradient(fill_rect.topLeft(), fill_rect.bottomLeft())
        gradient.setColorAt(0.0, fluid_color.lighter(125))
        gradient.setColorAt(1.0, fluid_color.darker(110))

        painter.setBrush(QBrush(gradient))
        painter.drawRoundedRect(fill_rect, 14, 14)

        bulb_gradient = QLinearGradient(
            center_x - bulb_radius,
            bulb_center_y - bulb_radius,
            center_x + bulb_radius,
            bulb_center_y + bulb_radius
        )
        bulb_gradient.setColorAt(0.0, fluid_color.lighter(120))
        bulb_gradient.setColorAt(1.0, fluid_color.darker(110))

        painter.setPen(QPen(QColor("#5d6e9e"), 2))
        painter.setBrush(QBrush(bulb_gradient))
        painter.drawEllipse(
            int(center_x - bulb_radius),
            int(bulb_center_y - bulb_radius),
            bulb_radius * 2,
            bulb_radius * 2
        )

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255, 65))
        painter.drawEllipse(
            int(center_x - bulb_radius + 12),
            int(bulb_center_y - bulb_radius + 14),
            14,
            14
        )

        main_pen = QPen(QColor("#e1e7ff"), 2)
        small_pen = QPen(QColor("#7c89b5"), 1)

        tick_values = [100, 75, 50, 25, 0, -25, -50]

        for value in tick_values:
            tick_ratio = (value + 50.0) / 150.0
            y = tube_rect.bottom() - tube_height * tick_ratio

            if value in [100, 50, 0, -50]:
                painter.setPen(main_pen)
                painter.drawLine(
                    int(center_x + 42),
                    int(y),
                    int(center_x + 62),
                    int(y)
                )

                text = f"{value:+d}°" if value != 0 else "0°"
                painter.drawText(
                    int(center_x + 72),
                    int(y + 5),
                    text
                )
            else:
                painter.setPen(small_pen)
                painter.drawLine(
                    int(center_x + 44),
                    int(y),
                    int(center_x + 56),
                    int(y)
                )


class Some(QMainWindow):
    def __init__(self):
        super().__init__()

        self.myClsig = cl1.mySignal
        self.data = Data()

        self.setWindowTitle("FCSGID_Lab2")
        self.resize(1120, 700)

        self.central = QWidget()
        self.setCentralWidget(self.central)

        self.main_layout = QVBoxLayout(self.central)
        self.main_layout.setContentsMargins(24, 22, 24, 18)
        self.main_layout.setSpacing(16)

        self.content_layout = QHBoxLayout()
        self.content_layout.setSpacing(22)
        self.main_layout.addLayout(self.content_layout)

        self.left_panel = QFrame()
        self.left_panel.setObjectName("panel")
        self.left_panel.setMinimumWidth(430)

        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(24, 18, 24, 20)
        self.left_layout.setSpacing(10)

        self.left_title = QLabel("ГРАДУСНИК")
        self.left_title.setObjectName("sectionTitle")
        self.left_title.setAlignment(Qt.AlignCenter)

        self.thermometer = ThermometerWidget()

        self.temperature_label = QLabel()
        self.temperature_label.setObjectName("temperatureLabel")
        self.temperature_label.setAlignment(Qt.AlignCenter)

        self.left_layout.addWidget(self.left_title)

        self.left_layout.addWidget(
            self.thermometer, 0, Qt.AlignHCenter
        )
        self.left_layout.addSpacing(2)
        self.left_layout.addWidget(self.temperature_label)
        self.left_layout.addStretch()

        self.right_panel = QFrame()
        self.right_panel.setObjectName("panel")
        self.right_panel.setMinimumWidth(620)

        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(22, 18, 22, 20)
        self.right_layout.setSpacing(16)

        self.right_title = QLabel("ТЕМПЕРАТУРА")
        self.right_title.setObjectName("sectionTitle")

        self.c_input = QDoubleSpinBox()
        self.f_input = QDoubleSpinBox()
        self.k_input = QDoubleSpinBox()

        fields = [
            (self.c_input, " °C", -50.0, 100.0),
            (self.f_input, " °F", -58.0, 212.0),
            (self.k_input, " K", 223.15, 373.15)
        ]

        for field, suffix, minimum, maximum in fields:
            field.setRange(minimum, maximum)
            field.setDecimals(2)
            field.setSingleStep(0.1)
            field.setSuffix(suffix)
            field.setMinimumHeight(46)
            field.setButtonSymbols(QDoubleSpinBox.UpDownArrows)

        values = cl1.func(self.data)
        self.c_input.setValue(values[0])
        self.f_input.setValue(values[1])
        self.k_input.setValue(values[2])

        self.row_c = self.createInputRow("Цельсий", self.c_input)
        self.row_f = self.createInputRow("Фаренгейт", self.f_input)
        self.row_k = self.createInputRow("Кельвин", self.k_input)

        self.reset_button = QPushButton("Вернуть исходные данные")
        self.reset_button.setObjectName("resetButton")
        self.reset_button.setCursor(Qt.PointingHandCursor)
        self.reset_button.setMinimumHeight(52)

        self.right_layout.addWidget(self.right_title)
        self.right_layout.addWidget(self.row_c)
        self.right_layout.addWidget(self.row_f)
        self.right_layout.addWidget(self.row_k)
        self.right_layout.addStretch()
        self.right_layout.addWidget(self.reset_button)

        self.content_layout.addWidget(self.left_panel, 5)
        self.content_layout.addWidget(self.right_panel, 6)

        self.footer_label = QLabel(
            "Введите температуру в допустимом диапазоне: от -50 °C до +100 °C (!)"
        )
        self.footer_label.setObjectName("footerLabel")
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.footer_label)

        self.c_input.valueChanged.connect(self.myClsig.emit)
        self.f_input.valueChanged.connect(cl2.mySignal.emit)
        self.k_input.valueChanged.connect(self.from_kelvin)

        self.myClsig.connect(self.from_celsius)
        cl2.mySignal.connect(self.from_fahrenheit)
        self.reset_button.clicked.connect(self.reset_values)

        self.update_visuals(values[0])
        self.apply_styles()

    def createInputRow(self, text, field):
        row = QFrame()
        row.setObjectName("inputRow")

        layout = QHBoxLayout(row)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(18)

        label = QLabel(text)
        label.setObjectName("rowLabel")
        label.setMinimumWidth(150)

        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(field, 1)

        return row

    def from_celsius(self, value):
        self.update_values(value)

    def from_fahrenheit(self, value):
        celsius = (value - 32) * 5 / 9
        self.update_values(celsius)

    def from_kelvin(self, value):
        celsius = value - 273.15
        self.update_values(celsius)

    def update_values(self, celsius):
        self.data.setData(celsius)
        values = self.data.getData()

        fields = [
            self.c_input,
            self.f_input,
            self.k_input
        ]

        for field, value in zip(fields, values):
            field.blockSignals(True)
            field.setValue(value)
            field.blockSignals(False)

        self.update_visuals(celsius)

    def update_visuals(self, celsius):
        self.thermometer.setTemperature(celsius)
        self.temperature_label.setText(
            f"{celsius:.2f} °C".replace(".", ",")
        )

    def reset_values(self):
        self.update_values(20.0)

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #111833;
            }

            QWidget {
                color: #f3f1ff;
                font-family: "Segoe UI";
                font-size: 11pt;
            }

            QFrame#panel {
                background-color: #232b52;
                border: 1px solid #394479;
                border-radius: 22px;
            }

            QLabel#sectionTitle {
                font-size: 13pt;
                font-weight: 700;
                color: #f0b7ff;
                letter-spacing: 1px;
            }

            QLabel#temperatureLabel {
                font-size: 27pt;
                font-weight: 700;
                color: #ffd27c;
                padding-top: 0px;
                padding-bottom: 4px;
            }

            QFrame#inputRow {
                background-color: #2f3762;
                border: 1px solid #415090;
                border-radius: 16px;
            }

            QLabel#rowLabel {
                font-size: 12pt;
                font-weight: 600;
                color: #ffffff;
            }

            QDoubleSpinBox {
                background-color: #1f2646;
                border: 1px solid #6273bd;
                border-radius: 10px;
                padding: 6px 10px;
                color: #ffffff;
                min-width: 180px;
                font-size: 12pt;
            }

            QDoubleSpinBox:focus {
                border: 2px solid #b48cff;
                background-color: #252d55;
            }

            QPushButton#resetButton {
                background-color: #7b63c9;
                border: none;
                border-radius: 14px;
                color: white;
                font-size: 12pt;
                font-weight: 700;
                padding: 10px 16px;
            }

            QPushButton#resetButton:hover {
                background-color: #8b71df;
            }

            QPushButton#resetButton:pressed {
                background-color: #6950ba;
            }

            QLabel#footerLabel {
                color: #d9dfff;
                font-size: 10.5pt;
                padding-top: 2px;
            }
        """)


class Data:
    def __init__(self):
        self.myData = []
        self.setData(20.0)

    def getData(self):
        return self.myData

    def setData(self, celsius):
        self.myData[:] = [
            celsius,
            celsius * 9 / 5 + 32,
            celsius + 273.15
        ]


def main():
    app = QApplication(sys.argv)

    window = Some()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
