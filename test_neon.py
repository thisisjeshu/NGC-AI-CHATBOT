import os
from sqlalchemy import create_engine, text

url = os.environ["DATABASE_URL"]

engine = create_engine(url)

with engine.connect() as conn:
    print("Database:", conn.execute(text("SELECT current_database()")).scalar())
    print("Test:", conn.execute(text("SELECT 1")).scalar())
