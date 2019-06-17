import threading
import time
import localGPS
import inertialSensors
import singleMotor
import random
import os


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
                speed = 1300  # 1500 + random.randint(-500, 600)
                motor.run_motor(speed)
                # print("=> {}".format(speed))

            time.sleep(0.05)
            print("LocalGPS: {}".format(self.local_gps.get_data()))
            print("InertialSensors: {}".format(self.inertial_sensors.get_data()))
            motors_list = []
            for motor in self.motors:
                motors_list.append(motor.get_current_speed())
            print("Motor: {}".format(motors_list))
            time.sleep(0.05)

    def stop(self):
        self.is_running = False
        self.local_gps.stop()
        self.inertial_sensors.stop()
        for motor in self.motors:
            motor.stop()

    def __del__(self):
        # self.stop()
        pass

    def config(self):
        try:
            os.system("sudo pigpiod -p 8888")
            time.sleep(1)
        except:
            pass
        self.local_gps = localGPS.LocalGPSThread()
        self.local_gps.config()
        self.inertial_sensors = inertialSensors.InertialSensorsThread()
        self.inertial_sensors.config()
        for index in range(self.count_motors):
            motor = singleMotor.SingleMotorThread()
            motor.config(port=8888, esc_pin=17+index, min_speed=1000, max_speed=2000)
            self.motors.append(motor)


if __name__ == "__main__":
    app = MainThread()
    app.config()
    app.start()

    time.sleep(5)

    app.stop()
    # while True:
    #     time.sleep(0.1)
