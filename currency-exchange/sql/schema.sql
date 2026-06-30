-- BRONZE LAYER
CREATE TABLE IF NOT EXISTS raw_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fetch_date TEXT NOT NULL,
    base_currency TEXT NOT NULL,
    raw_json TEXT NOT NULL,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SILVER LAYER
CREATE TABLE IF NOT EXISTS cleaned_rates (
    date TEXT NOT NULL,
    base_currency TEXT NOT NULL,
    target_currency TEXT NOT NULL,
    exchange_rate REAL NOT NULL,
    load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (date, base_currency, target_currency)
);

-- GOLD LAYER DIMENSIONS
CREATE TABLE IF NOT EXISTS dim_currencies (
    currency_code TEXT PRIMARY KEY,
    name TEXT,
    symbol TEXT,
    country TEXT
);

CREATE TABLE IF NOT EXISTS dim_dates (
    date TEXT PRIMARY KEY,
    year INTEGER,
    month INTEGER,
    day INTEGER,
    is_weekday INTEGER
);

-- GOLD LAYER FACTS
CREATE TABLE IF NOT EXISTS aggregated_rates (
    date TEXT NOT NULL,
    base_currency TEXT NOT NULL,
    target_currency TEXT NOT NULL,
    exchange_rate REAL NOT NULL,
    rate_change_pct REAL,
    rolling_avg REAL,
    PRIMARY KEY (date, base_currency, target_currency),
    FOREIGN KEY (target_currency) REFERENCES dim_currencies(currency_code),
    FOREIGN KEY (date) REFERENCES dim_dates(date)
);
