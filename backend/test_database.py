from sqlalchemy import text

from backend.database import engine


try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        print("PostgreSQL connection successful!")
        print(result.scalar())

except Exception as e:
    print("Database connection failed:")
    print(e)