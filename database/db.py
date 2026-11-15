
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import DATABASE_URL, create_required_directories


# Create required project directories
create_required_directories()


# Database connection
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)


# Create database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base class for database models
Base = declarative_base()


def get_db():
    """
    Provide a database session.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Create all registered database tables.
    """

    import database.models  # Register ORM models

    Base.metadata.create_all(bind=engine)

    print("SmartOMR AI database tables created successfully!")

if __name__ == "__main__":
    init_db()
