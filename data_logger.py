import time
import csv
from drivers.mpu6050 import MPU6050

# Initialize sensor
mpu = MPU6050()

# ==============================
# USER INPUT
# ==============================
label = int(input("Enter label (0 = Normal, 1 = Fault): "))
filename = input("Enter filename (example: data.csv): ")

samples = 200        # FIXED
sampling_rate = 500  # Hz
interval = 1.0 / sampling_rate

print("\nStarting data collection...")
time.sleep(2)

# ==============================
# DATA COLLECTION
# ==============================

data = []

for i in range(samples):
    t = time.time()

    ax, ay, az = mpu.read_accel()
    gx, gy, gz = mpu.read_gyro()

    # Convert to real units
    ax /= 16384.0
    ay /= 16384.0
    az /= 16384.0

    gx /= 131.0
    gy /= 131.0
    gz /= 131.0

    data.append([t, ax, ay, az, gx, gy, gz, label])

    time.sleep(interval)

# ==============================
# SAVE CSV AFTER COLLECTION
# ==============================

with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)

    # Header
    writer.writerow(["timestamp", "ax", "ay", "az", "gx", "gy", "gz", "label"])

    # Data
    writer.writerows(data)

print(f"\n✅ Dataset generated successfully: {filename}")
print(f"📊 Total samples: {samples}")
