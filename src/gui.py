from PyQt5 import QtWidgets, QtCore
import math

import config
from src import motorControl


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.motors = [motorControl.MotorController(*motor) for motor in config.Changer.motors]

        self.motor_bar = MotorBar(self.motors)

        for motor in self.motors:
            motor.start_poll()

        self.setCentralWidget(self.motor_bar)
        self.show()


class MotorBar(QtWidgets.QWidget):
    def __init__(self, motor_controllers):
        super().__init__()

        self._layout = QtWidgets.QHBoxLayout()
        for motor_controller in motor_controllers:
            self._layout.addWidget(MotorView(motor_controller))
        self.setLayout(self._layout)


class MotorView(QtWidgets.QGroupBox):
    def __init__(self, motor_controller):
        super().__init__()

        self.motor_controller = motor_controller

        self.setTitle(motor_controller.motor_name)

        self.hardware_buttons = []

        self.pos_view = PositionView(self.motor_controller.pos_changed, self.motor_controller.move_to, self.hardware_buttons)
        self.step_view = StepView(self.motor_controller.move_steps, self.hardware_buttons)
        self.go_limit_view = GoLimitView(self.motor_controller.go_to_cw, self.motor_controller.go_to_ccw, self.hardware_buttons)
        self.speed_view = SpeedView(self.motor_controller.speed_changed, self.motor_controller.set_speed, self.hardware_buttons)
        self.recall_position_view = RecallPositionView(self.pos_view.viewer)

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.addWidget(self.pos_view, 0)
        self._layout.addWidget(self.step_view, 0)
        self._layout.addWidget(self.go_limit_view, 0)
        self._layout.addWidget(self.speed_view, 0)
        self._layout.addWidget(self.recall_position_view, 0)

        self.setLayout(self._layout)


class PositionView(QtWidgets.QGroupBox):
    def __init__(self, pos_changed_signal, go_to_method, hardware_buttons):
        super(PositionView, self).__init__()
        self.setTitle("Position:")

        self.viewer = QtWidgets.QDoubleSpinBox()
        self.viewer.setRange(-99999999, 99999999)
        self.viewer.setDecimals(4)
        self.viewer.setSuffix("mm")
        self.go_button = QtWidgets.QPushButton("Go!")

        self._layout = QtWidgets.QHBoxLayout()
        self._layout.addWidget(self.viewer)
        self._layout.addWidget(self.go_button)

        self.setLayout(self._layout)

        self.hardware_buttons = hardware_buttons
        self.hardware_buttons.append(self.go_button)

        self.go_to_method = go_to_method
        pos_changed_signal.connect(self.pos_changed)
        self.go_button.clicked.connect(lambda: disable_buttons(self.hardware_buttons, self.change_pos))

    def pos_changed(self, pos):
        self.viewer.setValue(pos)

    def change_pos(self):
        self.go_to_method(self.viewer.value())


class StepView(QtWidgets.QGroupBox):
    def __init__(self, move_steps_method, hardware_buttons):
        super(StepView, self).__init__()
        self.setTitle("Step:")

        self.viewer = LogSpinBox()
        self.viewer.setRange(1, 99999999)
        self.viewer.setSuffix(" steps")
        self.viewer.setDecimals(0)
        self.viewer.setValue(100)
        self.step_up_button = QtWidgets.QPushButton("Step up")
        self.step_down_button = QtWidgets.QPushButton("Step down")

        self._layout = QtWidgets.QGridLayout()
        self._layout.addWidget(self.viewer, 0, 0, 2, 1)
        self._layout.addWidget(self.step_up_button, 0, 1)
        self._layout.addWidget(self.step_down_button, 1, 1)
        self.setLayout(self._layout)

        self.hardware_buttons = hardware_buttons
        self.hardware_buttons.append(self.step_up_button)
        self.hardware_buttons.append(self.step_down_button)

        self.move_steps_method = move_steps_method
        self.step_up_button.clicked.connect(lambda: disable_buttons(self.hardware_buttons, self.step_up))
        self.step_down_button.clicked.connect(lambda: disable_buttons(self.hardware_buttons, self.step_down))

    def step_up(self):
        self.move_steps_method(self.viewer.value())

    def step_down(self):
        self.move_steps_method(-self.viewer.value())


class GoLimitView(QtWidgets.QGroupBox):
    def __init__(self, go_to_cw_method, go_to_ccw_method, hardware_buttons):
        super(GoLimitView, self).__init__()
        self.setTitle("Go to limit:")

        self.CW_button = QtWidgets.QPushButton("CW")
        self.CCW_button = QtWidgets.QPushButton("CCW")

        self._layout = QtWidgets.QHBoxLayout()
        self._layout.addWidget(self.CW_button)
        self._layout.addWidget(self.CCW_button)
        self.setLayout(self._layout)

        self.hardware_buttons = hardware_buttons
        self.hardware_buttons.append(self.CW_button)
        self.hardware_buttons.append(self.CCW_button)

        self.CW_button.clicked.connect(lambda: disable_buttons(self.hardware_buttons, go_to_cw_method))
        self.CCW_button.clicked.connect(lambda: disable_buttons(self.hardware_buttons, go_to_cw_method))


class SpeedView(QtWidgets.QGroupBox):
    def __init__(self, speed_changed_signal, set_speed_method, hardware_buttons):
        super(SpeedView, self).__init__()
        self.setTitle("Speed:")

        self.speed_viewer = LogSpinBox()
        self.speed_viewer.setRange(0, 99999999)
        self.speed_viewer.setSuffix(" steps/s")
        self.set_speed_button = QtWidgets.QPushButton("Set speed")

        self._layout = QtWidgets.QHBoxLayout()
        self._layout.addWidget(self.speed_viewer)
        self._layout.addWidget(self.set_speed_button)
        self.setLayout(self._layout)

        self.hardware_buttons = hardware_buttons
        self.hardware_buttons.append(self.set_speed_button)

        self.set_speed_method = set_speed_method
        speed_changed_signal.connect(self.speed_changed)
        self.set_speed_button.clicked.connect(lambda: disable_buttons(self.hardware_buttons, self.change_speed))

    def speed_changed(self, speed):
        self.speed_viewer.setValue(speed)

    def change_speed(self):
        self.set_speed_method(self.speed_viewer.value())


class RecallPositionView(QtWidgets.QGroupBox):
    def __init__(self, pos_view):
        super(RecallPositionView, self).__init__()
        self.setTitle("Recall Position:")

        self.saved_pos = 0
        self.pos_viewer = QtWidgets.QLineEdit("0")
        self.pos_viewer.setDisabled(True)
        self.save_pos_button = QtWidgets.QPushButton("Save Position")
        self.recall_pos_button = QtWidgets.QPushButton("Recall Position")

        self._layout = QtWidgets.QGridLayout()
        self._layout.addWidget(self.pos_viewer, 0, 0, 2, 1)
        self._layout.addWidget(self.save_pos_button, 0, 1)
        self._layout.addWidget(self.recall_pos_button, 1, 1)
        self.setLayout(self._layout)

        self._reference_pos_view = pos_view

        self.save_pos_button.clicked.connect(self.save_position)
        self.recall_pos_button.clicked.connect(self.recall_position)

    def save_position(self):
        self.saved_pos = self._reference_pos_view.value()
        self.pos_viewer.setText("{:.2f}".format(self.saved_pos))

    def recall_position(self):
        self._reference_pos_view.setValue(self.saved_pos)


class LogSpinBox(QtWidgets.QDoubleSpinBox):
    def stepBy(self, amount):
        if amount == 1:
            val = self.value()*2
        elif amount == -1:
            val = self.value()/2
        else:
            raise ValueError("this function should get 1 or -1")

        if val == 0:
            val = 1

        self.setValue(round(val, -int(math.floor(math.log10(abs(val))))))


class DisableButtons:
    def __init__(self, buttons):
        self.buttons = buttons

    def __enter__(self):
        for button in self.buttons:
            button.setEnabled(False)

    def __exit__(self, exc_type, exc_val, exc_tb):
        for button in self.buttons:
            button.setEnabled(True)


def disable_buttons(buttons, function):
    with DisableButtons(buttons):
        function()
