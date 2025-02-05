from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DB_PATH = "backend/ao3_scheduler.db"
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define Fic Model with all AO3 required fields
class ScheduledFic(Base):
    __tablename__ = "scheduled_fics"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    fandoms = Column(String, nullable=False)  # Comma-separated
    rating = Column(String, nullable=False)
    warnings = Column(String, nullable=False)
    category = Column(String, nullable=False)
    language = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    content = Column(String, nullable=False)  # Fic text
    tags = Column(String, nullable=True)  # Comma-separated
    relationships = Column(String, nullable=True)  # Comma-separated
    characters = Column(String, nullable=True)  # Comma-separated
    author_notes = Column(String, nullable=True)
    end_notes = Column(String, nullable=True)
    is_complete = Column(Boolean, default=False)
    scheduled_time = Column(DateTime, nullable=False)
    status = Column(String, default="pending")  # "pending" -> "posted"

# Create tables if they don't exist
def init_db():
    if not os.path.exists(DB_PATH):  # Avoid re-creating DB every time
        Base.metadata.create_all(bind=engine)

init_db()
