import sys
import os
from sqlalchemy import text
from app.db.session import engine

def alter_db():
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE clippings ADD COLUMN custom_layout JSON;"))
            conn.commit()
            print("Successfully added custom_layout to clippings")
    except Exception as e:
        print(f"Column might already exist or error: {e}")

if __name__ == "__main__":
    alter_db()
