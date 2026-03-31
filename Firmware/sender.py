# sender.py - Run on Windows PC
# Sends CPU/GPU usage and temps to the XIAO over USB serial
#
# Install dependencies:
#   pip install psutil pyserial gputil

import psutil
import serial
import time
import GPUtil

PORT = "COM3"   # <- Change to your XIAO's COM port (check Device Manager)
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)  # wait for XIAO to boot

print(f"Connected on {PORT}. Sending stats...")

while True:
    # CPU usage
    cpu_pct = psutil.cpu_percent(interval=0.5)

    # CPU temp
    cpu_temp = 0.0
    try:
        temps = psutil.sensors_temperatures()
        if "coretemp" in temps:
            cpu_temp = temps["coretemp"][0].current
        elif "cpu_thermal" in temps:
            cpu_temp = temps["cpu_thermal"][0].current
    except Exception:
        pass

    # GPU usage + temp
    gpu_pct  = 0.0
    gpu_temp = 0.0
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu_pct  = gpus[0].load * 100
            gpu_temp = gpus[0].temperature
    except Exception:
        pass

    line = f"{cpu_pct:.1f},{gpu_pct:.1f},{cpu_temp:.1f},{gpu_temp:.1f}\n"
    ser.write(line.encode())
    print(f"Sent: {line.strip()}")

    time.sleep(0.5)
