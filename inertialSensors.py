import threading
import time
import subprocess


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
            self.orientation = data_int[:3]
            self.acceleration = data_int[3:6]
            self.magnetometer = data_int[6:]

    def stop(self):
        self.is_running = False

    def __del__(self):
        self.stop()

    def config(self):
        self.sensor_path = '/home/pi/minimu9-ahrs/minimu9-ahrs --output euler'.split()

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


if __name__ == "__main__":
    app = InertialSensorsThread()
    app.config()
    app.start()

    while True:
        time.sleep(0.1)
        print("Data: {}".format(app.get_data()))
