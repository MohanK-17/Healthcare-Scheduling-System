# app/test/test_con.py
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from app.core.config import settings

try:
    # Use sslmode=require for Render PostgreSQL
    engine = create_engine(settings.DATABASE_URL + "?sslmode=require")
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))  
        print("Connection successful:", result.fetchone())
except OperationalError as e:
    print("Connection failed:", e)
