import threading
import time


class InertialSensorsThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.is_running = False
        self.gyro_x = 0
        self.gyro_y = 0
        self.gyro_z = 0

    def run(self):
        print("Start inertial sensors thread")
        self.is_running = True

        while self.is_running:
            self.convert_data()
            time.sleep(0.1)

    def stop(self):
        self.is_running = False

    def __del__(self):
        self.stop()

    def config(self):
        pass

    def convert_data(self):
        pass

    def get_data(self):
        obj = dict()
        obj["gyro_x"] = self.gyro_x
        obj["gyro_y"] = self.gyro_y
        obj["gyro_z"] = self.gyro_z
        return obj


if __name__ == "__main__":
    app = InertialSensorsThread()
    app.config()
    app.start()

    while True:
        time.sleep(0.1)
        print("Data: {}".format(app.get_data()))
