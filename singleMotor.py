import threading
import time
import pigpio
import os


class SingleMotorThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.is_running = False
        self.esc = None
        self.pi = None
        self.min_speed = None
        self.max_speed = None
        self.current_speed = None

    def run(self):
        print("Start single motor thread")
        self.is_running = True
        while self.is_running:
            time.sleep(0.1)

    def stop(self):
        self.is_running = False
        self.current_speed = 0
        if self.is_running:
            self.pi.set_servo_pulsewidth(self.esc, self.current_speed)
            self.pi.stop()

    def __del__(self):
        self.stop()

    def config(self, port, esc_pin, min_speed, max_speed):
        # os.system("sudo pigpiod -p 8890")
        # time.sleep(1)
        self.esc = esc_pin
        self.current_speed = 0
        self.pi = pigpio.pi(port=port)
        self.pi.set_servo_pulsewidth(self.esc, self.current_speed)
        self.min_speed = min_speed if min_speed else 1000
        self.max_speed = max_speed if max_speed else 2000

    def run_motor(self, value):
        if self.is_running:
            speed = value
            speed = speed if speed > self.min_speed else self.min_speed
            speed = speed if speed < self.max_speed else self.max_speed
            self.current_speed = speed
            self.pi.set_servo_pulsewidth(self.esc, self.current_speed)

    def get_current_speed(self):
        return self.current_speed


if __name__ == "__main__":
    app = SingleMotorThread()
    app.config(8892, 4, 1100, 2000)
    app.start()

    i = 1000
    while True:
        time.sleep(1)
        app.run_motor(i)
        print("Speed: {}".format(app.get_current_speed()))
        i += 100
        if i > 2500:
            app.stop()
