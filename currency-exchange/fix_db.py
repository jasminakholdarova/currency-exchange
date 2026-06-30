import sqlite3
import sys
import os

# Ensure we are in a clean state
if os.path.exists('currency_pipeline.db'):
    os.remove('currency_pipeline.db')

conn = sqlite3.connect('currency_pipeline.db')
cursor = conn.cursor()

try:
    # 1. Read and execute your schema.sql file to build the tables
    with open('sql/schema.sql', 'r') as f:
        cursor.executescript(f.read())
    print("Database tables successfully built from schema.sql!")

    # 2. Add the pipeline folder to the path and seed dimensions
    sys.path.append(os.path.abspath('pipeline'))
    from transform_gold import populate_dimensions
    populate_dimensions(cursor)
    
    conn.commit()
    print("Database setup complete and dimensions seeded!")
except Exception as e:
    print(f"Error occurred: {e}")
finally:
    conn.close()
