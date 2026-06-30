import os
import sqlite3
import pytest
from datetime import datetime

def test_database_initialization():
    """Verify that execution layers are set up properly."""
    db_name = "test_env.db"
    if os.path.exists(db_name):
        os.remove(db_name)
        
    conn = sqlite3.connect(db_name)
    with open('sql/schema.sql', 'r') as f:
        conn.executescript(f.read())
        
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cursor.fetchall()]
    
    assert "raw_rates" in tables
    assert "cleaned_rates" in tables
    assert "aggregated_rates" in tables
    
    conn.close()
    os.remove(db_name)
    