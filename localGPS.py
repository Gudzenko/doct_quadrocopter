import threading
import time
import serial
import os
import re
import struct


class LocalGPSThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.is_running = False
        self.serial = None
        self.data = b""
        self.x = 0
        self.y = 0
        self.z = 0

    def run(self):
        print("Start local GPS thread")
        self.is_running = True
        self.data = b""
        self.x = 0
        self.y = 0
        self.z = 0
        self.run_local_gps()

    def stop(self):
        self.is_running = False

    def __del__(self):
        self.stop()
        self.serial.close()

    def run_local_gps(self):
        while self.is_running:
            self.convert_data()
            time.sleep(0.05)

    def config(self, baud_rate=57600):
        try:
            os.system("sudo chmod 666 /dev/ttyS0")
            self.serial = serial.Serial("/dev/ttyS0", baud_rate, timeout=0.2)
        except Exception as e:
            time.sleep(0.3)
            print("try again config")
            self.config()

    def add_data(self, data):
        self.data += data
        protocols = [
            {
                "header": b'\xff\x47\x11\x00\x16',
                "length": 29,
                "name": "coordinates",
            },
            {
                "header": b'\xff\x47\x06\x00\x10',
                "length": 23,
                "name": "telemetry data",
            },
            {
                "header": b'\xff\x47\x12\x00',
                "length": 64,
                "name": "resolution coordinates",
            },
        ]
        for protocol in protocols:
            is_has = True
            while is_has:
                # print("Data: " + str(self.data))
                result = re.search(protocol["header"], self.data)
                start_index = result.start() if result else -1
                if start_index > -1 and start_index + protocol["length"] <= len(self.data):
                    is_has = True
                    select_protocol = self.data[start_index:start_index + protocol["length"]]
                    self.data = self.data[:start_index] + self.data[start_index + protocol["length"]:]
                    if protocol["name"] == "coordinates":
                        code1, code2, code3, code4, timestamp, x, y, z, flags, address, orient, t, crc = struct.unpack("<BBHBIiiiBBHHH", select_protocol)
                        # print((timestamp / 1000000.0, x / 1000.0, y / 1000.0, z / 1000.0, flags))
                        if flags == 2:
                            self.x = x / 1000.0
                            self.y = y / 1000.0
                            self.z = z / 1000.0

                else:
                    is_has = False

    def convert_data(self):
        try:
            num = 0
            num = self.serial.in_waiting
        except Exception as e:
            print(e)
            print(num)
            num = 0
            time.sleep(0.2)
        if num > 0:
            received_data = self.serial.read(num)
            # print("[{}] {}".format(num, received_data))
            self.add_data(received_data)
        else:
            pass
            # print("Zero")
            #time.sleep(0.03)
            #self.serial.reset_input_buffer()
            self.serial.close()
            #time.sleep(0.03)
            self.config()
            #self.serial.open()

    def get_data(self):
        obj = dict()
        obj["x"] = self.x
        obj["y"] = self.y
        obj["z"] = -1 * self.z
        return obj


if __name__ == "__main__":
    app = LocalGPSThread()
    app.config()
    app.start()
    while True:
        time.sleep(0.3)
        print("Position: {}".format(app.get_data()))
