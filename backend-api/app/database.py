from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./securizz.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_hash = Column(String, unique=True, index=True)
    source_code = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditReport(Base):
    __tablename__ = "audit_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, index=True)
    report_hash = Column(String, unique=True, index=True)
    ipfs_cid = Column(String)
    risk_score = Column(Float)
    vulnerabilities = Column(Text)
    mitigation_strategies = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, index=True)
    user_feedback = Column(Text)
    accuracy_rating = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)
