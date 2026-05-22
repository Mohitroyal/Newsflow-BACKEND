import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

db_url = settings.DATABASE_URL
# Strip unsupported query parameters like ?pgbouncer=true
if "?" in db_url:
    db_url = db_url.split("?")[0]

import sys
is_testing = "pytest" in sys.modules or "unittest" in sys.modules or os.environ.get("TESTING") == "1"

if is_testing:
    db_url = "sqlite:///./test_temp.db"
elif "sqlite" not in db_url:
    try:
        import socket
        host = db_url.split("@")[-1].split(":")[0].split("/")[0]
        port_str = db_url.split(":")[-1].split("/")[0]
        port = int(port_str) if port_str.isdigit() else 5432
        socket.create_connection((host, port), timeout=2)
    except Exception:
        print(f"[WARNING] PostgreSQL host {host}:{port} is unreachable. Falling back to local SQLite.")
        db_url = "sqlite:///./newscraft.db"

print("DATABASE_URL =", os.environ.get("DATABASE_URL"))
print("Parsed DB URL =", db_url)

if db_url.startswith("sqlite"):
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine(db_url, pool_pre_ping=True)
    print("Database engine initialized successfully.")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
