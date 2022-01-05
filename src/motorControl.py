import tango
from PyQt5.QtCore import QEventLoop, QTimer, pyqtSignal, QObject

from config import config


class MotorController(QObject):

    pos_changed = pyqtSignal(float)
    speed_changed = pyqtSignal(float)
    moveFinished = pyqtSignal()

    def __init__(self, motor_name, motor_address):
        super().__init__()
        self.motor_name = motor_name
        self.last_pos = 0
        self.last_speed = 0
        self.motor_move_started = False

        self.motor = tango.DeviceProxy(config["tango_server"] + motor_address)

    def start_poll(self):
        self._timer = QTimer()
        self._timer.timeout.connect(self.update)
        self._timer.start(1000 / config["polling_rate_hz"])

    def move_to(self, pos):
        self.motor.position = pos
        self.motor_move_started = True
        self.wait(config["timeout_ms"], self.moveFinished)

    def move_steps(self, steps):
        self.motor.setupstepmove(self.motor.StepPositionInternal+steps)
        self.motor.startmove()
        self.motor_move_started = True
        self.wait(config["timeout_ms"], self.moveFinished)

    def go_to_cw(self):
        self.motor.moveToCwLimit()
        self.motor_move_started = True
        self.wait(config["timeout_ms"], self.moveFinished)

    def go_to_ccw(self):
        self.motor.moveToCcwLimit()
        self.motor_move_started = True
        self.wait(config["timeout_ms"], self.moveFinished)

    def set_speed(self, speed):
        self.motor.slewrate = speed

    def wait(self, timeout, signal=None):
        loop = QEventLoop()
        QTimer.singleShot(timeout, loop.quit)
        if signal is not None:
            signal.connect(loop.quit)

        loop.exec()

    def stop(self):
        self.motor.StopMove()

    def update(self):
        new_pos = self.motor.position
        if new_pos != self.last_pos:
            self.pos_changed.emit(new_pos)
            self.last_pos = new_pos

        new_speed = self.motor.slewrate
        if new_speed != self.last_speed:
            self.speed_changed.emit(new_speed)
            self.last_speed = new_speed

        if self.motor_move_started and self.motor.state() == tango.DevState.ON:
            self.moveFinished.emit()
            self.motor_move_started = False
