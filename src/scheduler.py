import schedule
import time
import subprocess
import sys

def run_project():
    print("\nRunning Business Anomaly Detection Project...\n")

    subprocess.run(
        [sys.executable, "main.py"],
        cwd="src"
    )

schedule.every(1).minutes.do(run_project)

print("Scheduler Started...")
print("Project will run every 1 minute for testing...")

while True:
    schedule.run_pending()
    time.sleep(1)