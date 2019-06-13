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


for line in run_process('/home/pi/minimu9-ahrs/minimu9-ahrs --output euler'.split()):
    # print(line)
    data = line[:-1].split()
    # print(data)
    data_int = [float(i) for i in data]
    print(data_int)

