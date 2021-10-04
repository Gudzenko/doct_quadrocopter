import threading
import time
import subprocess
import math
import os
from filter import Filter


class InertialSensorsThread(threading.Thread):
    def __init__(self, save_to_file=False):
        threading.Thread.__init__(self)
        self.is_running = False
        dt = 0.02
        self.is_new = True
        self.acceleration = []
        self.filter_acceleration = Filter(size=3, dt=dt, t=0.04)
        self.orientation = []
        self.filter_orientation = Filter(size=3, dt=dt, t=0.04)
        self.magnetometer = []
        self.filter_magnetometer = Filter(size=3, dt=dt, t=0.04)
        self.gyro = []
        self.filter_gyro = Filter(size=3, dt=dt, t=0.04)
        self.sensor_path = None
        self.time = 0.0
        self.time_start = 0.0
        self.save_to_file = save_to_file
        if self.save_to_file:
            self.file_name = "inertialSensorsLogs.csv"
            self.file = open(self.file_name, "w")

    def run(self):
        print("Start inertial sensors thread")
        self.is_running = True
        self.acceleration = [0, 0, 0]
        self.orientation = [0, 0, 0]
        self.magnetometer = [0, 0, 0]
        self.gyro = [0, 0, 0]
        self.time_start = time.time()
        self.time = self.time_start
        for line in self.convert_data(self.sensor_path):
            # print(line)
            if not self.is_running:
                break
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
            self.filter_gyro.add(self.gyro)
            self.orientation = orientation
            self.filter_orientation.add(self.orientation)
            self.acceleration = data_int[4:7]
            self.filter_acceleration.add(self.acceleration)
            self.magnetometer = data_int[7:]
            self.filter_magnetometer.add(self.magnetometer)
            if self.save_to_file:
                self.to_file()

    def to_file(self):
        data_to_file = ""

        data_to_file += "Orientation;"
        for item in list(self.orientation):
            data_to_file += " {:8.3f};".format(item)

        data_to_file += "OrientationFilter;"
        for item in list(self.filter_orientation.get()):
            data_to_file += " {:8.3f};".format(item)
            
        data_to_file += "OrientationPrediction;"
        for item in list(self.filter_orientation.prediction(t=None)):
            data_to_file += " {:8.3f};".format(item)

        data_to_file += "Acceleration;"
        for item in list(self.acceleration):
            data_to_file += " {:8.5f};".format(item)

        data_to_file += "AccelerationFilter;"
        for item in list(self.filter_acceleration.get()):
            data_to_file += " {:8.5f};".format(item)

        data_to_file += "AccelerationPrediction;"
        for item in list(self.filter_acceleration.prediction(t=None)):
            data_to_file += " {:8.5f};".format(item)

        data_to_file += "Gyro;"
        for item in list(self.gyro):
            data_to_file += " {:8.5f};".format(item)

        data_to_file += "GyroFilter;"
        for item in list(self.filter_gyro.get()):
            data_to_file += " {:8.5f};".format(item)

        data_to_file += "Magnetometer;"
        for item in list(self.magnetometer):
            data_to_file += " {:8.3f};".format(item)

        data_to_file += "MagnetometerFilter;"
        for item in list(self.filter_magnetometer.get()):
            data_to_file += " {:8.3f};".format(item)

        self.file.write("Time;  {:12.6f}; ; {} ; \n".format(self.time - self.time_start, data_to_file))

    def stop(self):
        self.is_running = False
        if self.save_to_file:
            self.save_to_file = False
            self.file.close()
            self.file = open(self.file_name, "r")
            data = self.file.read()
            new_data = data.replace(".", ",")
            self.file.close()
            self.file = open(self.file_name, "w")
            self.file.write(new_data)
            self.file.close()
        print('Stop')

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
    try:
        os.system("sudo pigpiod -p 8888")
        time.sleep(1)
    except:
        pass
    app = InertialSensorsThread(save_to_file=True)
    app.config()
    app.start()

    t = 0.0
    while t < 10:
        time.sleep(0.01)
        t += 0.01
        data = app.get_data()
        orient = (data[0])["orientation"]
        print("Data: time={:10.2f} x={:9.3f} y={:9.3f} z={:9.3f} is_new={}".format(data[2], orient[0], orient[1], orient[2], data[1]))
        # print("Data: {}".format((app.get_data())))
    app.stop()
