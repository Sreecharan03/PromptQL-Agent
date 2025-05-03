# my_agent/utils/db.py

import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

# 1. Define your schemas and seed data in one place
TABLE_SCHEMAS = {
    "users": {
        "create": """
            CREATE TABLE IF NOT EXISTS users (
                id     INTEGER PRIMARY KEY AUTOINCREMENT,
                name   TEXT,
                email  TEXT
            );
        """,
        "seed": [
            ("Alice", "alice@example.com"),
            ("Bob",   "bob@example.com"),
            ("Carol", "carol@example.com"),
            ("Dave",  "dave@example.com"),
            ("Eve",   "eve@example.com"),
        ],
    },
    "orders": {
        "create": """
            CREATE TABLE IF NOT EXISTS orders (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id  INTEGER,
                total    REAL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
        """,
        "seed": [
            (1,  123.45),
            (2,   67.89),
            (3,  250.00),
            (1,   75.25),
        ],
    },
}

# 2. Read the path from ENV or default
DB_PATH = os.getenv("DB_PATH", "data/app.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# 3. Open the database connection
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

def init_database():
    """
    Create all tables defined in TABLE_SCHEMAS and seed them if empty.
    """
    for table_name, info in TABLE_SCHEMAS.items():
        # Create the table if it doesn't exist
        cursor.execute(info["create"])
        # Check if the table is empty
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        # Seed only when empty
        if count == 0 and info.get("seed"):
            # Build placeholders for seed rows (NULL for the auto-id)
            sample_row = info["seed"][0]
            placeholders = ", ".join("?" for _ in sample_row)
            insert_sql = f"INSERT INTO {table_name} VALUES (NULL, {placeholders})"
            cursor.executemany(insert_sql, info["seed"])
    conn.commit()
