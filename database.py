
import sqlite3
from pathlib import Path
from datetime import datetime, timezone


# Database file will be created in the project folder.
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "healthcare_chatbot.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


# --------------------------------------------------
# INITIALIZE DATABASE
# --------------------------------------------------

def initialize_database():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                intent TEXT,
                confidence REAL,
                created_at TEXT NOT NULL
            )
        """)

        connection.commit()

    finally:
        connection.close()

    print("SQLite database initialized successfully!")


# --------------------------------------------------
# SAVE MESSAGE
# --------------------------------------------------

def save_message(user_message, bot_response, intent, confidence):

    connection = get_connection()

    try:
        cursor = connection.cursor()

        created_at = datetime.now(timezone.utc).isoformat()

        cursor.execute("""
            INSERT INTO chat_messages (
                user_message,
                bot_response,
                intent,
                confidence,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_message,
            bot_response,
            intent,
            confidence,
            created_at
        ))

        connection.commit()

    finally:
        connection.close()


# --------------------------------------------------
# GET CHAT HISTORY
# --------------------------------------------------

def get_chat_history():

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                user_message,
                bot_response,
                intent,
                confidence,
                created_at
            FROM chat_messages
            ORDER BY id ASC
            LIMIT 100
        """)

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


# --------------------------------------------------
# CLEAR CHAT HISTORY
# --------------------------------------------------

def clear_chat_history():

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("DELETE FROM chat_messages")

        connection.commit()

    finally:
        connection.close()
