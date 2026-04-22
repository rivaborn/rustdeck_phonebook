#!/usr/bin/env python3
"""
Seed script for the RustDesk Phone Book application.
This script populates the database with sample computer records.
"""

import os
import sys
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Add the src directory to the path so we can import the models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from phonebook.models import Computer

# Create database engine and session
DATABASE_URL = "sqlite:///./phonebook.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def seed_sample_data():
    """Seed the database with sample computer records."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session
    db = SessionLocal()
    
    try:
        # Check if there are already records
        existing_records = db.query(Computer).count()
        if existing_records > 0:
            print("Database already seeded with records. Skipping...")
            return
        
        # Sample computer records
        sample_computers = [
            Computer(
                name="Work Laptop",
                hostname="work-laptop",
                ip_address="192.168.1.101",
                rustdesk_id="123456789",
                location="Office A",
                notes="Primary work machine"
            ),
            Computer(
                name="Home Desktop",
                hostname="home-desktop",
                ip_address="192.168.1.102",
                rustdesk_id="987654321",
                location="Living Room",
                notes="Used for personal projects"
            ),
            Computer(
                name="Server Room PC",
                hostname="server-pc",
                ip_address="192.168.1.103",
                rustdesk_id="456789123",
                location="Server Room",
                notes="Production server"
            ),
            Computer(
                name="Development VM",
                hostname="dev-vm",
                ip_address="192.168.1.104",
                rustdesk_id="321654987",
                location="Development",
                notes="Testing environment"
            ),
            Computer(
                name="Backup Server",
                hostname="backup-server",
                ip_address="192.168.1.105",
                rustdesk_id="654321789",
                location="Server Room",
                notes="Backup and archive"
            )
        ]
        
        # Add records to database
        for computer in sample_computers:
            db.add(computer)
        
        db.commit()
        print(f"Successfully seeded database with {len(sample_computers)} sample records")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_sample_data()
