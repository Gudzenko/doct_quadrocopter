import threading
import time
import subprocess
import math
import os


class InertialSensorsThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.is_running = False
        self.is_new = True
        self.acceleration = []
        self.orientation = []
        self.magnetometer = []
        self.gyro = []
        self.sensor_path = None
        self.time = 0.0

    def run(self):
        print("Start inertial sensors thread")
        self.is_running = True
        self.acceleration = [0, 0, 0]
        self.orientation = [0, 0, 0]
        self.magnetometer = [0, 0, 0]
        self.gyro = [0, 0, 0]
        self.time = time.time()
        for line in self.convert_data(self.sensor_path):
            # print(line)
            next_time = time.time()
            dt = next_time - self.time
            self.time = next_time
            data = line[:-1].split()
            data_int = [float(i) for i in data]
            # print("{}".format(data_int))
            orientation = self.quaternion2euler(data_int[:4])
            # self.orientation[0] = data_int[2]
            # self.orientation[1] = data_int[1]
            # self.orientation[2] = data_int[0]
            for index in range(3):
                self.gyro[index] = (orientation[index] - self.orientation[index]) / dt * math.pi / 180.0
            self.is_new = True
            self.orientation = orientation
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
        is_new = self.is_new
        obj["acceleration"] = self.acceleration
        obj["orientation"] = self.orientation
        obj["magnetometer"] = self.magnetometer
        obj["gyro"] = self.gyro
        self.is_new = False
        return (obj, is_new, self.time)

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
        time.sleep(0.01)
        data = app.get_data()
        orient = (data[0])["orientation"]
        print("Data: time={:10.2f} x={:9.3f} y={:9.3f} z={:9.3f} is_new={}".format(data[2], orient[0], orient[1], orient[2], data[1]))
        # print("Data: {}".format((app.get_data())))
