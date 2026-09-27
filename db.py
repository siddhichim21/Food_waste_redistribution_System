import os
import mysql.connector

# Prefer environment variables so the real password isn't hard-coded in
# source control; falls back to your original value if none are set.
DB_CONFIG = {
    "host": os.environ.get("FDS_DB_HOST", "localhost"),
    "user": os.environ.get("FDS_DB_USER", "root"),
    "password": os.environ.get("FDS_DB_PASSWORD", "!Sisa@21#"),
    "database": os.environ.get("FDS_DB_NAME", "food_donation"),
}


def get_connection():
    """Return a new MySQL connection. Raises the underlying exception on failure."""
    return mysql.connector.connect(**DB_CONFIG)


if __name__ == "__main__":
    # Quick manual connectivity check: `python db.py`
    try:
        conn = get_connection()
        print("Database connected successfully!")
        conn.close()
    except Exception as e:
        print("Connection failed:", e)
