from backend.database import Base, engine

# Import models so SQLAlchemy knows about them
from backend import models


print("Creating database tables...")

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")