from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Computer(Base):
    __tablename__ = "computers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    friendly_name = Column(String, nullable=False)
    rustdesk_id = Column(String, nullable=False, unique=True)
    hostname = Column(String, nullable=True)
    local_ip = Column(String, nullable=True)
    operating_system = Column(String, nullable=True)
    username = Column(String, nullable=True)
    location = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    tags = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
