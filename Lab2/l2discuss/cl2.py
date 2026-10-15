from PyQt5.QtCore import QObject, pyqtSignal


class SignalContainer(QObject):
    mySignal = pyqtSignal(float)


signal_owner = SignalContainer()
mySignal = signal_owner.mySignal
