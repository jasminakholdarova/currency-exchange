import time
import schedule
import logging
import subprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_daily_job():
    logging.info("Scheduler triggered the daily run!")
    # Runs our primary data runner script for today's metrics
    subprocess.run(["python", "pipeline/load_bronze.py", "--latest"])

# 8:00 AM Tashkent Time (UTC+5) is exactly 3:00 AM UTC.
schedule.every().day.at("03:00").do(run_daily_job)

logging.info("Scheduler started. Running automatically at 08:00 AM Tashkent Time daily...")

while True:
    schedule.run_pending()
    time.sleep(60)
    