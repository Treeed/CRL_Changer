from src import motorControl


class Changer:
    tango_server = 'haspp02oh1:10000/'
    motors = [
        motorControl.MotorController("ich_bin_ein_motor", "p02/motor/elab.10"),
        motorControl.MotorController("ich auch", "p02/motor/elab.11"),
    ]
    timeout_ms = 120000
    polling_rate_hz = 5
