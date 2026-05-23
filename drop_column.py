import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"Connecting to database to drop hashed_password...")
engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS hashed_password;"))
        conn.commit()
        print("Successfully dropped 'hashed_password' column.")
    except Exception as e:
        print(f"Error dropping column: {e}")
