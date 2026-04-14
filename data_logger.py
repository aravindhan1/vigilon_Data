import time
import csv
import math
from drivers.mpu6050 import MPU6050

# -----------------------------
# SETTINGS
# -----------------------------
TOTAL_SAMPLES = 1000
BASELINE_SAMPLES = 100          # keep sensor still at start

SAMPLE_RATE = 100
DT = 1.0 / SAMPLE_RATE

# Vibration detection tuning
CONSECUTIVE_HITS = 2
PRE_FAULT_WINDOW = 25           # relabel a short window before detection as fault

# -----------------------------
# MPU6050
# -----------------------------
mpu = MPU6050()

# -----------------------------
# FILE NAME
# -----------------------------
filename = input("Enter output CSV filename (example: dataset.csv): ").strip()
if not filename:
    filename = "dataset.csv"

print("\nKeep the sensor still now.")
print(f"Collecting {BASELINE_SAMPLES} baseline samples...")
time.sleep(2)

rows = []
baseline_scores = []
fault_latched = False
hit_count = 0
fault_start_index = None

# -----------------------------
# HELPERS
# -----------------------------
def read_mpu():
    ax, ay, az = mpu.read_accel()
    gx, gy, gz = mpu.read_gyro()

    # Convert raw counts to physical units
    ax /= 16384.0
    ay /= 16384.0
    az /= 16384.0

    gx /= 131.0
    gy /= 131.0
    gz /= 131.0

    return ax, ay, az, gx, gy, gz

def compute_score(ax, ay, az, gx, gy, gz, base_vib_mean):
    vib = math.sqrt(ax * ax + ay * ay + az * az)
    gyro_mag = math.sqrt(gx * gx + gy * gy + gz * gz)
    # Combined motion score
    score = abs(vib - base_vib_mean) + 0.25 * gyro_mag
    return vib, score

# -----------------------------
# COLLECTION LOOP
# -----------------------------
for i in range(TOTAL_SAMPLES):
    t = round(i * DT, 6)

    ax, ay, az, gx, gy, gz = read_mpu()

    vib = math.sqrt(ax * ax + ay * ay + az * az)

    # Baseline phase: label = 0
    if i < BASELINE_SAMPLES:
        label = 0
        baseline_scores.append(vib)

        if i == BASELINE_SAMPLES - 1:
            base_vib_mean = sum(baseline_scores) / len(baseline_scores)
            base_vib_std = (
                sum((x - base_vib_mean) ** 2 for x in baseline_scores) / len(baseline_scores)
            ) ** 0.5

            # Threshold tuned for tap/vibration detection
            threshold = base_vib_mean + (4.0 * base_vib_std) + 0.15

            print("\nBaseline complete.")
            print("Now tap or hit the sensor to induce fault.")
            print(f"Detection threshold: {threshold:.4f}\n")

    else:
        # Fault detection phase
        vib_now, score = compute_score(ax, ay, az, gx, gy, gz, base_vib_mean)

        if fault_latched:
            label = 1
        else:
            if score > threshold:
                hit_count += 1
            else:
                hit_count = 0

            if hit_count >= CONSECUTIVE_HITS:
                fault_latched = True
                fault_start_index = max(0, len(rows) - PRE_FAULT_WINDOW + 1)
                print(f"Fault detected at sample {i}. Latching label = 1.")
                label = 1
            else:
                label = 0

    # Store row
    rows.append([t, ax, ay, az, gx, gy, gz, vib, label])

    # Keep the loop close to target rate
    time.sleep(DT)

# -----------------------------
# RETROACTIVE RELABELING
# -----------------------------
# If fault was detected, mark a short window before detection as fault too
if fault_start_index is not None:
    for j in range(fault_start_index, len(rows)):
        rows[j][-1] = 1

# -----------------------------
# SAVE CSV
# -----------------------------
with open(filename, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["time", "ax", "ay", "az", "gx", "gy", "gz", "vib", "label"])
    writer.writerows(rows)

print(f"\nDataset saved: {filename}")
print(f"Total samples: {len(rows)}")
print("Done.")
