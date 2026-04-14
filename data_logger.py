import time
import csv
import math
from drivers.mpu6050 import MPU6050

# ==============================
# SETTINGS
# ==============================
TOTAL_SAMPLES = 1000
SAMPLE_RATE = 100          # 100 Hz → ~10 seconds
DT = 1.0 / SAMPLE_RATE

BASELINE_SAMPLES = 100     # first 1 sec for normal baseline
CONSECUTIVE_HITS = 2       # avoid noise

# ==============================
# INIT SENSOR
# ==============================
mpu = MPU6050()

filename = input("Enter output filename (example: dataset.csv): ").strip()
if not filename:
    filename = "dataset.csv"

print("\nKeep sensor still... collecting baseline")
time.sleep(2)

rows = []
baseline_vib = []
hit_count = 0

# ==============================
# READ FUNCTION
# ==============================
def read_mpu():
    ax, ay, az = mpu.read_accel()
    gx, gy, gz = mpu.read_gyro()

    # Convert to real units
    ax /= 16384.0
    ay /= 16384.0
    az /= 16384.0

    gx /= 131.0
    gy /= 131.0
    gz /= 131.0

    return ax, ay, az, gx, gy, gz

# ==============================
# MAIN LOOP
# ==============================
start_time = time.time()

for i in range(TOTAL_SAMPLES):

    loop_start = time.time()

    # time column like your dataset
    t = round(i * DT, 6)

    ax, ay, az, gx, gy, gz = read_mpu()

    # vibration magnitude
    vib = math.sqrt(ax**2 + ay**2 + az**2)

    # --------------------------
    # BASELINE PHASE
    # --------------------------
    if i < BASELINE_SAMPLES:
        label = 0
        baseline_vib.append(vib)

        if i == BASELINE_SAMPLES - 1:
            base_mean = sum(baseline_vib) / len(baseline_vib)
            base_std = (
                sum((x - base_mean) ** 2 for x in baseline_vib) / len(baseline_vib)
            ) ** 0.5

            threshold = base_mean + (4 * base_std) + 0.15

            print("\nBaseline complete.")
            print("Now tap or hit the sensor to create faults.")
            print(f"Threshold = {threshold:.4f}\n")

    # --------------------------
    # FAULT DETECTION
    # --------------------------
    else:
        gyro_mag = math.sqrt(gx**2 + gy**2 + gz**2)

        # combined score
        score = abs(vib - base_mean) + 0.25 * gyro_mag

        if score > threshold:
            hit_count += 1
        else:
            hit_count = 0

        if hit_count >= CONSECUTIVE_HITS:
            label = 1
        else:
            label = 0

    # store row
    rows.append([t, ax, ay, az, gx, gy, gz, vib, label])

    # --------------------------
    # TIMING CONTROL
    # --------------------------
    elapsed = time.time() - loop_start
    if elapsed < DT:
        time.sleep(DT - elapsed)

# ==============================
# SAVE CSV
# ==============================
with open(filename, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["time", "ax", "ay", "az", "gx", "gy", "gz", "vib", "label"])
    writer.writerows(rows)

print(f"\n✅ Dataset saved: {filename}")
print(f"📊 Total samples: {TOTAL_SAMPLES}")
print(f"⏱ Duration ≈ {TOTAL_SAMPLES / SAMPLE_RATE:.2f} seconds")
