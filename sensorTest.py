#!/usr/bin/python
import subprocess
import time


def run_process(exe):
    p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        # returns None while subprocess is running
        retcode = p.poll()
        line = p.stdout.readline()
        yield line
        if retcode is not None:
            break


index = 0
current_time = time.time()
for line in run_process('/home/pi/minimu9-ahrs/minimu9-ahrs --output euler'.split()):
    # print(line)
    data = line[:-1].split()
    # print(data)
    data_int = [float(i) for i in data]
    index += 1
    if index % 1000 == 0:
        t = time.time()
        print("Time: {}".format(t - current_time))
        print("Hrz: {}".format(1000.0 / (t - current_time)))
        current_time = t
    # print(data_int)

