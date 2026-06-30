import os
import sqlite3
import json
import logging

DB_NAME = os.getenv("DB_NAME", "currency_pipeline.db")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_bronze_to_silver():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, raw_json FROM raw_rates")
    rows = cursor.fetchall()
    
    inserted_count = 0
    for row_id, raw_json in rows:
        data = json.loads(raw_json)
        date = data.get("date")
        base = data.get("base")
        rates = data.get("rates", {})
        
        for target, rate in rates.items():
            if rate is None or rate <= 0:
                logging.warning(f"Skipping invalid rate: {target} -> {rate} on {date}")
                continue
                
            try:
                cursor.execute(
                    """INSERT OR IGNORE INTO cleaned_rates (date, base_currency, target_currency, exchange_rate)
                       VALUES (?, ?, ?, ?)""",
                    (date, base, target, float(rate))
                )
                if cursor.rowcount > 0:
                    inserted_count += 1
            except Exception as e:
                logging.error(f"Error parsing record ID {row_id}: {e}")
                
    conn.commit()
    conn.close()
    logging.info(f"Silver Layer updated. {inserted_count} new entries processed.")

if __name__ == "__main__":
    process_bronze_to_silver() 