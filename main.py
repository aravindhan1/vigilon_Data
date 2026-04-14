# main.py

from drivers.mpu6050 import MPU6050
from drivers.ds18b20 import DS18B20
import time

mpu = MPU6050()
temp_sensor = DS18B20()

while True:
    ax, ay, az = mpu.read_accel()
    gx, gy, gz = mpu.read_gyro()
    temp = temp_sensor.read_temp()

    print("------ SENSOR DATA ------")
    print(f"Temperature: {temp:.2f} °C")
    print(f"Accel: X={ax}, Y={ay}, Z={az}")
    print(f"Gyro: X={gx}, Y={gy}, Z={gz}")

    time.sleep(1)
