import sys
import os
import argparse
import logging
import sqlite3
import requests
import json
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_currency_data(date_str):
    """Fetches exchange rates from Frankfurter API with USD as base."""
    url = f"https://api.frankfurter.dev/v1/{date_str}"
    params = {
        "base": "USD",
        "symbols": "UZS,RUB,EUR,GBP"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Failed to fetch data for {date_str}: Status {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Network error on {date_str}: {e}")
        return None

def run_pipeline_for_date(conn, date_str):
    logging.info(f"--- Running Pipeline for: {date_str} ---")
    
    # 1. BRONZE LAYER (Extract)
    data = fetch_currency_data(date_str)
    if not data:
        logging.warning(f"No data available for {date_str}. Skipping.")
        return
        
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO raw_rates (fetch_date, base_currency, raw_json) VALUES (?, ?, ?)",
        (date_str, "USD", json.dumps(data))
    )
    conn.commit()
    logging.info(f"Loaded raw JSON for {date_str} into Bronze.")
    
    # 2. SILVER LAYER (Cleanse)
    rates = data.get("rates", {})
    base = data.get("base", "USD")
    actual_date = data.get("date", date_str)
    
    new_entries = 0
    for curr, rate in rates.items():
        if rate > 0:
            cursor.execute("""
                INSERT OR IGNORE INTO cleaned_rates (date, base_currency, target_currency, exchange_rate)
                VALUES (?, ?, ?, ?)
            """, (actual_date, base, curr, float(rate)))
            if cursor.rowcount > 0:
                new_entries += 1
    conn.commit()
    logging.info(f"Silver Layer updated. {new_entries} new entries processed.")
    
    # 3. GOLD LAYER (Analytics)
    cursor.execute("""
        INSERT OR REPLACE INTO aggregated_rates (date, base_currency, target_currency, exchange_rate, rate_change_pct, rolling_avg)
        SELECT 
            date, 
            base_currency, 
            target_currency, 
            exchange_rate,
            0.0,
            exchange_rate
        FROM cleaned_rates
        WHERE date = ?
    """, (actual_date,))
    conn.commit()
    logging.info("Gold Layer metrics successfully calculated.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--backfill", type=int, help="Number of days to backfill")
    parser.add_argument("--latest", action="store_true", help="Run for today")
    args = parser.parse_args()
    
    conn = sqlite3.connect("currency_pipeline.db")
    
    # Auto-initialize schema tables if database was wiped
    with open("sql/schema.sql", "r") as f:
        conn.executescript(f.read())
        
    if args.backfill:
        logging.info(f"Starting backfill for {args.backfill} days...")
        for i in range(args.backfill, -1, -1):
            target_date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            run_pipeline_for_date(conn, target_date)
    elif args.latest:
        today_str = datetime.now().strftime("%Y-%m-%d")
        run_pipeline_for_date(conn, today_str)
        
    conn.close()
