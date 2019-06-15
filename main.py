import threading
import time
import localGPS
import inertialSensors
import singleMotor
import random


class MainThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.is_running = False
        self.local_gps = None
        self.inertial_sensors = None
        self.motors = []
        self.count_motors = 4

    def run(self):
        print("Start main thread")
        self.is_running = True
        self.local_gps.start()
        self.inertial_sensors.start()
        for motor in self.motors:
            motor.start()

        time.sleep(1)
        while self.is_running:
            for motor in self.motors:
                speed = 1500 + random.randint(-500, 600)
                motor.run_motor(speed)
                # print("=> {}".format(speed))

            time.sleep(0.05)
            print("LocalGPS: {}".format(self.local_gps.get_data()))
            print("InertialSensors: {}".format(self.inertial_sensors.get_data()))
            for motor in self.motors:
                print("Motor: {}".format(motor.get_current_speed()))
            time.sleep(0.05)

    def stop(self):
        self.is_running = False
        self.local_gps.stop()
        self.inertial_sensors.stop()
        for motor in self.motors:
            motor.stop()

    def __del__(self):
        self.stop()

    def config(self):
        self.local_gps = localGPS.LocalGPSThread()
        self.local_gps.config()
        self.inertial_sensors = inertialSensors.InertialSensorsThread()
        self.inertial_sensors.config()
        for index in range(self.count_motors):
            motor = singleMotor.SingleMotorThread()
            motor.config(port=8890, esc_pin=4+index, min_speed=1100, max_speed=2000)
            self.motors.append(motor)


if __name__ == "__main__":
    app = MainThread()
    app.config()
    app.start()

    while True:
        time.sleep(0.1)
