import threading
import time
import subprocess
import math
import os


class InertialSensorsThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.is_running = False
        self.acceleration = []
        self.orientation = []
        self.magnetometer = []
        self.sensor_path = None

    def run(self):
        print("Start inertial sensors thread")
        self.is_running = True
        self.acceleration = [0, 0, 0]
        self.orientation = [0, 0, 0]
        self.magnetometer = [0, 0, 0]
        for line in self.convert_data(self.sensor_path):
            data = line[:-1].split()
            data_int = [float(i) for i in data]
            # print("{}".format(data_int))
            self.orientation = self.quaternion2euler(data_int[:4])
            # self.orientation[0] = data_int[2]
            # self.orientation[1] = data_int[1]
            # self.orientation[2] = data_int[0]
            self.acceleration = data_int[4:7]
            self.magnetometer = data_int[7:]

    def stop(self):
        self.is_running = False

    def __del__(self):
        self.stop()

    def config(self):
        # self.sensor_path = '/home/pi/minimu9-ahrs/minimu9-ahrs --output euler'.split()
        self.sensor_path = '/home/pi/minimu9-ahrs/minimu9-ahrs --output quaternion'.split()

    def convert_data(self, exe):
        p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while self.is_running:
            return_code = p.poll()
            line = p.stdout.readline()
            yield line
            if return_code is not None:
                break

    def get_data(self):
        obj = dict()
        obj["acceleration"] = self.acceleration
        obj["orientation"] = self.orientation
        obj["magnetometer"] = self.magnetometer
        return obj

    def quaternion2euler(self, q):
        euler = [0, 0, 0]
        if len(q) != 4:
            print("=============ERROR {}".format(q))
            return euler
        try:
            euler[0] = math.atan2(2 * (q[0] * q[1] + q[2] * q[3]), 1 - 2 * (q[1] * q[1] + q[2] * q[2]))
            value = 2 * (q[0] * q[2] - q[1] * q[3])
            euler[1] = math.asin(value if math.fabs(value) < 1 else math.copysign(1.0, value))
            euler[2] = math.atan2(2 * (q[0] * q[3] + q[1] * q[2]), 1 - 2 * (q[2] * q[2] + q[3] * q[3]))
        except Exception as e:
            print("Error: {}".format(e))
            euler = [0, 0, 0]
        for index, e in enumerate(euler):
            euler[index] = e * 180.0 / math.pi
        return euler


if __name__ == "__main__":
    app = InertialSensorsThread()
    app.config()
    app.start()

    while True:
        time.sleep(0.1)
        print("Data: {}".format((app.get_data())["orientation"]))
