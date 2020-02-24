import inertialSensors
import singleMotor
import time
import os


if __name__ == "__main__":
    try:
        os.system("sudo pigpiod -p 8888")
        time.sleep(1)
    except:
        pass
    app_sensor = inertialSensors.InertialSensorsThread(save_to_file=True)
    app_sensor.config()
    app_sensor.start()
    
    pins = [5, 6, 13, 19]
    app = []
    for index in range(4):
        app.append(singleMotor.SingleMotorThread())
        app[index].config(8888, pins[index], 800, 2000)
        app[index].start()
    time.sleep(0.5)
    
    value = 1300
    for index in range(4):
        app[index].run_motor(value)
        print("Speed {}: {}".format(index + 1, app[index].get_current_speed()))
        
    t = 0.0
    while t < 10:
        time.sleep(0.01)
        t += 0.01
        data = app_sensor.get_data()
        orient = (data[0])["orientation"]
        print("Data: time={:10.2f} x={:9.3f} y={:9.3f} z={:9.3f} is_new={}".format(data[2], orient[0], orient[1], orient[2], data[1]))
        # print("Data: {}".format((app.get_data())))
    app_sensor.stop()

    for index in range(4):
        app[index].run_motor(1000)
    time.sleep(0.1)
    