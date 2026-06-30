import os
import sqlite3
import logging
from datetime import datetime

DB_NAME = os.getenv("DB_NAME", "currency_pipeline.db")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def populate_dimensions(cursor):
    currencies = [
        ('UZS', 'Uzbekistan Som', 'soʻm', 'Uzbekistan'),
        ('RUB', 'Russian Ruble', '₽', 'Russia'),
        ('EUR', 'Euro', '€', 'Eurozone'),
        ('GBP', 'British Pound', '£', 'United Kingdom'),
        ('USD', 'US Dollar', '$', 'United States')
    ]
    cursor.executemany("INSERT OR IGNORE INTO dim_currencies VALUES (?, ?, ?, ?)", currencies)
    
    cursor.execute("SELECT DISTINCT date FROM cleaned_rates")
    dates = cursor.fetchall()
    for (d_str,) in dates:
        dt = datetime.strptime(d_str, "%Y-%m-%d")
        is_weekday = 1 if dt.weekday() < 5 else 0
        cursor.execute(
            "INSERT OR IGNORE INTO dim_dates VALUES (?, ?, ?, ?, ?)",
            (d_str, dt.year, dt.month, dt.day, is_weekday)
        )

def build_gold_facts():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    populate_dimensions(cursor)
    conn.commit()
    
    query = """
    WITH analytical_rates AS (
        SELECT 
            date,
            base_currency,
            target_currency,
            exchange_rate,
            LAG(exchange_rate) OVER (PARTITION BY base_currency, target_currency ORDER BY date) as prev_rate,
            AVG(exchange_rate) OVER (PARTITION BY base_currency, target_currency ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as seven_day_avg
        FROM cleaned_rates
    )
    SELECT 
        date, base_currency, target_currency, exchange_rate,
        CASE WHEN prev_rate IS NOT NULL THEN ((exchange_rate - prev_rate) / prev_rate) * 100 ELSE 0 END,
        seven_day_avg
    FROM analytical_rates;
    """
    cursor.execute(query)
    facts = cursor.fetchall()
    
    cursor.executemany(
        """INSERT OR REPLACE INTO aggregated_rates 
           (date, base_currency, target_currency, exchange_rate, rate_change_pct, seven_day_avg)
           VALUES (?, ?, ?, ?, ?, ?)""",
        facts
    )
    
    conn.commit()
    conn.close()
    logging.info("Gold Layer metrics successfully calculated.")

if __name__ == "__main__":
    build_gold_facts()


