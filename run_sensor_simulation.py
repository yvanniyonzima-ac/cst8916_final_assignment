import subprocess
import signal
import sys
import time

# List of your Python programs (replace with your actual script filenames)
scripts = ["dows_lake_sensor.py", "fifth_avenue_sensor.py", "nac_sensor.py"]

# Start each script as a subprocess
processes = []

python_version = "python3"

try:
    for script in scripts:
        print(f"Starting {script}...")
        proc = subprocess.Popen([python_version, script])
        processes.append(proc)

    print("All sensor simulation scripts are running. Press Ctrl+C to stop them...")

    # Keep the main thread alive
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\nCtrl+C detected. Terminating all scripts...")
    for proc in processes:
        proc.terminate()  # Sends SIGTERM
    for proc in processes:
        proc.wait()  # Waits for process to terminate
    print("All sensor simulation scripts have been stopped.")
    sys.exit(0)
