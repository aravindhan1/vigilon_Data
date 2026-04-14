# main.py

from drivers.mpu6050 import MPU6050

import time

mpu = MPU6050()

while True:
    ax, ay, az = mpu.read_accel()
    gx, gy, gz = mpu.read_gyro()

    print("------ SENSOR DATA ------")
    print(f"Accel: X={ax}, Y={ay}, Z={az}")
    print(f"Gyro: X={gx}, Y={gy}, Z={gz}")

    time.sleep(1)
