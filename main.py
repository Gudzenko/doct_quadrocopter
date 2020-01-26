import threading
import time
import localGPS
import inertialSensors
import singleMotor
import filter
import random
import os
import math


class MainThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.is_running = False
        self.local_gps = None
        self.inertial_sensors = None
        self.motors = []
        self.count_motors = 4
        self.gyro_filter = filter.Filter(size=3, coef=0.95)
        self.orientation_filter = filter.Filter(size=3, coef=0.95)
        self.position = {"x": 0, "y": 0, "z": 0}
        self.orientation = {"x": 0, "y": 0, "z": 0}
        self.trajectory = {"x": 0, "y": 0, "z": 0}
        self.gyro = {"x": 0, "y": 0, "z": 0}
        self.time = 0
        self.dtime = 0
        self.is_show_logs = False
        self.start_time = time.time()
        self.start_position = {"x": 0, "y": 0, "z": 0}
        self.t_full = 30
        self.max_angle = 60 * math.pi / 180.0
        self.file_name = "log.csv"
        self.file = open(self.file_name, "w")
        self.file_str = ""

    @staticmethod
    def to_rad(values):
        result = []
        for value in values:
            result.append(value * math.pi / 180.0)
        return result

    @staticmethod
    def to_degree(values):
        result = []
        for value in values:
            result.append(value / math.pi * 180.0)
        return result

    def read_sensors(self):
        self.position = self.local_gps.get_data()
        inertial_data = self.inertial_sensors.get_data()[0]
        self.orientation_filter.add(MainThread.to_rad(inertial_data["orientation"]))
        self.orientation = dict(zip(["x", "y", "z"], self.orientation_filter.get()))
        self.gyro_filter.add(inertial_data["gyro"])
        self.gyro = dict(zip(["x", "y", "z"], self.gyro_filter.get()))
        # print("LocalGPS: {}".format(self.position))
        # print("Orientation: {}".format(dict(zip(["x", "y", "z"], inertial_data["orientation"]))))
        self.file_str += " ;localGPS; {:8.4f}; {:8.4f}; {:8.4f};".format(self.position["x"], self.position["y"], self.position["z"])
        self.file_str += " ;Orientation; {:8.3f}; {:8.3f}; {:8.3f};".format(self.orientation["x"] * 180.0 / 3.14, self.orientation["y"] * 180.0 / 3.14, self.orientation["z"] * 180.0 / 3.14)
        self.file_str += " ;Gyro; {:8.5f}; {:8.5f}; {:8.5f};".format(self.gyro["x"], self.gyro["y"], self.gyro["z"])

    def calibrate_position(self):
        count = 30
        position = [0, 0, 0]
        for i in range(count):
            time.sleep(0.1)
            self.read_sensors()
            new_position = [self.position["x"], self.position["y"], self.position["z"]]
            for index, value in enumerate(position):
                position[index] += 1.0 / count * new_position[index]
        self.start_position = dict(zip(["x", "y", "z"], position))
        print("Start position: {}".format(self.start_position))

    def get_trajectory(self, t):
        x = 0
        y = 0
        z = 0
        force = 0
        dt = 8  # sec
        t_full = self.t_full
        h = 1
        if 0 <= t < dt:
            x = 0
            y = 0
            z = h * (t - 0) / dt
            force = (t - 0) / dt
        elif dt <= t < t_full - dt:
            x = 0
            y = 0
            z = h
            force = 1
        elif t_full - dt <= t < t_full:
            x = 0
            y = 0
            z = h * (t_full - 0 - t) / dt
            force = (t_full - 0 - t) / dt
        self.trajectory = {"x": x, "y": y, "z": z, "force": force}
        self.file_str += "; trajectory ; {:8.4f} ; {:8.4f} ; {:8.4f} ; {:8.4f};".format(x, y, z, force)
        # print("Trajectory: {}".format(self.trajectory))

    def set_motors(self, values):
        str_value = ""
        for index, motor in enumerate(self.motors):
            motor.run_motor(values[index])
            str_value += "{:7.2f} ".format(values[index])
        if self.is_show_logs:
            print("Motor: [{}]".format(str_value))
        self.file_str += "; motors ; {:6.1f}; {:6.1f}; {:6.1f}; {:6.1f} ; ".format(values[0], values[1], values[2], values[3])

    def control(self):
        trajectory = self.trajectory
        position = {
            "x": self.position["x"] - self.start_position["x"],
            "y": self.position["y"] - self.start_position["y"],
            "z": self.position["z"] - self.start_position["z"],
        }
        speed = {"x": 0, "y": 0, "z": 0}
        orientation = self.orientation
        # angular_velocity = {"x": 0, "y": 0, "z": 0}
        angular_velocity = self.gyro
        angular_velocity["z"] = 0

        tensor = [[0.005, 0, 0], [0, 0.005, 0], [0, 0, 0.01]]
        KK = 10.0
        K1 = 1.14 * math.pow(10, -6)
        K2 = 6.5 * math.pow(10, -6)  # 7
        L = 0.25
        mass = 1.25
        g = 9.8
        сoef = 1.0
        coef_gyro = 0.0

        i_x = tensor[0][0]
        i_y = tensor[1][1]
        i_z = tensor[2][2]

        k1a = KK / 5.0
        k1b = KK / 10.0
        k2a = KK / 5.0
        k2b = KK / 10.0
        k3a = KK / 10.0
        k4a = 9.0 / 4.0

        k11 = (k1a * k1a + 4 * k1a * k1b + k1b * k1b) * i_x
        k12 = 2 * i_x * (k1a + k1b) * coef_gyro
        k13 = i_x * k1a * k1a * k1b * k1b / g
        k14 = i_x * 2 * k1a * k1b * (k1a + k1b) / g

        k21 = (k2a * k2a + 4 * k2a * k2b + k2b * k2b) * i_y
        k22 = 2 * i_y * (k2a + k2b) * coef_gyro
        k23 = -1 * i_y * k2a * k2a * k2b * k2b / g
        k24 = -1 * i_y * 2 * k2a * k2b * (k2a + k2b) / g

        k31 = k3a * k3a * i_z
        k32 = 2 * k3a * i_z

        k41 = k4a * k4a
        k42 = 2 * k4a

        motors = [0, 0, 0, 0]

        motors[0] = mass * g - k41 * сoef * (position["z"] - trajectory["z"]) + k42 * speed["z"]
        motors[1] = -1 * (k11 * orientation["x"] + k12 * angular_velocity["x"] +
                          k13 * сoef * (position["y"] - trajectory["y"]) + k14 * speed["y"])
        motors[2] = -1 * (k21 * orientation["y"] + k22 * angular_velocity["y"] +
                          k23 * сoef * (position["x"] - trajectory["x"]) + k24 * speed["x"])
        motors[3] = -1 * (k31 * orientation["z"] + k32 * angular_velocity["z"])

        pwm = [0, 0, 0, 0]

        pwm[0] = motors[0] / 4.0 / K2 + motors[2] / 2.0 / L / K2 - motors[3] / 4.0 / K1
        pwm[1] = motors[0] / 4.0 / K2 - motors[2] / 2.0 / L / K2 - motors[3] / 4.0 / K1
        pwm[2] = motors[0] / 4.0 / K2 - motors[1] / 2.0 / L / K2 + motors[3] / 4.0 / K1
        pwm[3] = motors[0] / 4.0 / K2 + motors[1] / 2.0 / L / K2 + motors[3] / 4.0 / K1
        # print("PWM: {}".format(pwm))
        pwm[3] *= 1.1

        for index, p in enumerate(pwm):

            pwm[index] = (self.motors[index].max_speed - self.motors[index].min_speed) / 1000.0 * \
                         round(math.pow(p, 0.5)) * trajectory["force"] + self.motors[index].min_speed
        return pwm
        # values = []
        # for motor in self.motors:
        #     values.append(1300 + random.randint(-500, 600))
        # return values

    def start_devices(self):
        # self.local_gps.start()
        self.inertial_sensors.start()
        for motor in self.motors:
            motor.start()
        time.sleep(3)

    def run(self):
        print("Start main thread")
        self.is_running = True
        self.start_devices()

        print("Start calibration")
        self.calibrate_position()

        print("Start main process")
        self.time = 0
        self.start_time = time.time()

        iteration = 0

        while self.is_running:
            delay_time = 0.01
            # time.sleep(0.005)
            iteration += 1
            self.file_str = ""

            # Time
            current_time = time.time() - self.start_time
            dt_ = current_time - self.time
            time.sleep(0 if delay_time - dt_ < 0 else delay_time - dt_)  
            current_time = time.time() - self.start_time
            dt = current_time - self.time
            self.dtime += dt
            if self.dtime > 0.3:
                self.dtime -= 0.3
                self.is_show_logs = True
            self.time = current_time
            if self.is_show_logs:
                print("Time: {:9.3f} Iteration: {}".format(self.time, iteration))
            self.file_str += "time; {:11.5f} ; {:11.5f} ; {:11.5f}".format(self.time, dt_, dt)

            # Generate trajectory
            self.get_trajectory(self.time)

            # Read sensors
            self.read_sensors()

            # Calculate control
            speed = self.control()

            # Send control on motors
            self.set_motors(speed)

            self.file.write(self.file_str + " ; \n")

            self.is_show_logs = False
            # End of trajectory
            if self.time >= self.t_full:
                self.stop()

            # Orientation limits
            if math.fabs(self.orientation["x"]) > self.max_angle or math.fabs(self.orientation["y"]) > self.max_angle:
                self.stop()

    def stop(self):
        if self.is_running:
            self.is_running = False
            self.local_gps.stop()
            self.inertial_sensors.stop()
            self.set_motors([800, 800, 800, 800])
            self.file.close()
            print("Start save in file")
            self.file = open(self.file_name, "r")
            data = self.file.read()
            new_data = data.replace(".", ",")
            self.file.close()
            self.file = open(self.file_name, "w")
            self.file.write(new_data)
            self.file.close()
            print("Finished save in file")
            # for motor in self.motors:
            #     motor.stop()

    def __del__(self):
        self.stop()

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
        motors_pins = [5, 6, 13, 19]
        for index in range(self.count_motors):
            motor = singleMotor.SingleMotorThread()
            motor.config(port=8888, esc_pin=motors_pins[index], min_speed=800, max_speed=2000)
            self.motors.append(motor)


if __name__ == "__main__":
    app = MainThread()
    app.config()
    app.start()

    # time.sleep(app.t_full + 10)

    # app.stop()
    while True:
        time.sleep(0.1)
