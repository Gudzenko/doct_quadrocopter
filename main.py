import threading
import time
import localGPS


class MainThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.is_running = False
        self.local_gps = None

    def run(self):
        print("Start main thread")
        self.is_running = True
        self.local_gps.start()

        while self.is_running:
            print("LocalGPS: {}".format(self.local_gps.get_data()))
            time.sleep(0.1)

    def stop(self):
        self.is_running = False
        self.local_gps.stop()

    def __del__(self):
        self.stop()

    def config(self):
        self.local_gps = localGPS.LocalGPSThread()
        self.local_gps.config()


if __name__ == "__main__":
    app = MainThread()
    app.config()
    app.start()

    while True:
        time.sleep(0.1)
