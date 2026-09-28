import sqlite3
from pathlib import Path

DATABASE = Path("ai_studio.db")


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            google_id TEXT UNIQUE,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            avatar TEXT,
            plan TEXT DEFAULT 'free',
            video_limit INTEGER DEFAULT 0,
            video_used INTEGER DEFAULT 0,
            image_limit INTEGER DEFAULT 0,
            image_used INTEGER DEFAULT 0,
            is_blocked INTEGER DEFAULT 0,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan_name TEXT NOT NULL,
            price REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            receipt TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS generations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            generation_type TEXT NOT NULL,
            prompt TEXT,
            result_url TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    default_settings = [
        ("app_name", "AI Studio"),
        ("free_video_limit", "0"),
        ("free_image_limit", "0"),
        ("small_plan_price", "0"),
        ("medium_plan_price", "0"),
        ("large_plan_price", "0"),
        ("payment_card", ""),
    ]

    for key, value in default_settings:
        connection.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )

    connection.commit()
    connection.close()


if __name__ == "__main__":
    init_database()
    print("Database tayyor!")
