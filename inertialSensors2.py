import threading
import time
import math
from filter import Filter
from mpu6050 import mpu6050


class InertialSensors2Thread(threading.Thread):
    def __init__(self, save_to_file=False):
        threading.Thread.__init__(self)
        self.is_running = False
        dt = 0.01
        self.dt = dt
        self.sensor = mpu6050(0x68)
        self.is_new = True
        self.acceleration = []
        self.filter_acceleration = Filter(size=3, dt=dt, t=0.04)
        self.orientation = []
        self.filter_orientation = Filter(size=3, dt=dt, t=0.04)
        self.magnetometer = []
        self.filter_magnetometer = Filter(size=3, dt=dt, t=1.0)
        self.gyro = []
        self.filter_gyro = Filter(size=3, dt=dt, t=0.04)
        self.time = 0.0
        self.time_start = 0.0
        self.save_to_file = save_to_file
        if self.save_to_file:
            self.file_name = "inertialSensors2Logs.csv"
            self.file = open(self.file_name, "w")

    def run(self):
        print("Start inertial sensors2 thread")
        self.is_running = True
        self.acceleration = [0, 0, 0]
        self.orientation = [0, 0, 0]
        self.magnetometer = [0, 0, 0]
        self.gyro = [0, 0, 0]
        self.time_start = time.time()
        self.time = self.time_start
        while self.is_running:
            # print(line)
            if not self.is_running:
                break
            next_time = time.time()
            dt = next_time - self.time
            self.time = next_time
            data = self.sensor.get_all_data()
            self.acceleration[0] = data[0]["x"]
            self.acceleration[1] = data[0]["y"]
            self.acceleration[2] = data[0]["z"]
            self.filter_acceleration.add(self.acceleration)
            self.gyro[0] = data[1]["x"]
            self.gyro[1] = data[1]["y"]
            self.gyro[2] = data[1]["z"]
            self.filter_gyro.add(self.gyro)
            orientation = self.calc_orientation()

            self.is_new = True

            self.orientation = orientation
            self.filter_orientation.add(self.orientation)

            self.filter_magnetometer.add(self.magnetometer)
            if self.save_to_file:
                self.to_file()

            dt1 = time.time() - next_time
            time.sleep(self.dt - dt1 if self.dt - dt1 > 0 else 0)

    def dist(self, a, b):
        return math.sqrt(a * a + b * b)

    def get_y_rotation(self, x, y, z):
        radians = math.atan2(x, self.dist(y, z))
        return -math.degrees(radians)

    def get_x_rotation(self, x, y, z):
        radians = math.atan2(y, self.dist(x, z))
        return math.degrees(radians)

    def get_z_rotation(self, x, y, z):
        return 0

    def angle(self, prev, gyro, accel):
        return 0.98 * (prev + gyro * self.dt) + 0.02 * accel

    def calc_orientation(self):
        gyro = self.filter_gyro.get()
        orientation = self.orientation
        acc = self.filter_acceleration.get()
        Ux = self.angle(orientation[0], gyro[0], self.get_x_rotation(acc[0], acc[1], acc[2]))
        Uy = self.angle(orientation[1], gyro[1], self.get_y_rotation(acc[0], acc[1], acc[2]))
        Uz = self.angle(orientation[2], gyro[2], self.get_z_rotation(acc[0], acc[1], acc[2]))
        return [Ux, Uy, Uz]

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
        self.sensor.set_gyro_range(self.sensor.GYRO_RANGE_250DEG)
        self.sensor.set_accel_range(self.sensor.ACCEL_RANGE_2G)

    def get_data(self):
        obj = dict()
        is_new = self.is_new
        obj["acceleration"] = self.acceleration
        obj["orientation"] = self.orientation
        obj["magnetometer"] = self.magnetometer
        obj["gyro"] = self.gyro
        self.is_new = False
        return (obj, is_new, self.time)


if __name__ == "__main__":
    app = InertialSensors2Thread(save_to_file=True)
    app.config()
    app.start()
    
    sensor = mpu6050(0x68)
    t = 0.0
    dt = app.dt
    while t < 20:
        time.sleep(dt)
        t += dt

        data = app.get_data()
        orient = (data[0])["orientation"]
        print("Data: time={:10.2f} x={:9.3f} y={:9.3f} z={:9.3f} is_new={}".format(data[2], orient[0], orient[1], orient[2], data[1]))

    app.stop()
