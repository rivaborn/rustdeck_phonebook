"""
Seed data script for the RustDesk Phone Book application.

This script populates the database with sample computer records for testing
and demonstration purposes. It is idempotent and will skip records if a
rustdesk_id already exists.
"""

from phonebook.database import SessionLocal
from phonebook.crud import create_computer
from phonebook.schemas import ComputerCreate
from sqlalchemy.exc import IntegrityError

def seed_sample_data() -> None:
    """Seed the database with 5 sample computer records."""
    # Initialize database session
    db = SessionLocal()
    
    # Define sample computer data
    sample_computers = [
        ComputerCreate(
            friendly_name="Main Office Desktop",
            rustdesk_id="123456789",
            hostname="main-desktop",
            local_ip="192.168.1.100",
            operating_system="Ubuntu 22.04 LTS",
            username="john.doe",
            location="Main Office",
            notes="Primary workstation for office work",
            tags="desktop,office,ubuntu"
        ),
        ComputerCreate(
            friendly_name="Development Laptop",
            rustdesk_id="987654321",
            hostname="dev-laptop",
            local_ip="10.0.0.50",
            operating_system="Windows 11 Pro",
            username="jane.smith",
            location="Development Team",
            notes="Used for coding and testing",
            tags="laptop,development,win11"
        ),
        ComputerCreate(
            friendly_name="Server Room VM",
            rustdesk_id="555555555",
            hostname="server-vm",
            local_ip="172.16.0.10",
            operating_system="CentOS 8",
            username="admin",
            location="Server Room",
            notes="Virtual machine for testing",
            tags="server,vm,centos"
        ),
        ComputerCreate(
            friendly_name="Conference Room Display",
            rustdesk_id="111111111",
            hostname="conference-display",
            local_ip="192.168.2.200",
            operating_system="Windows 10",
            username="meeting",
            location="Conference Room",
            notes="Display for presentations",
            tags="display,conference,win10"
        ),
        ComputerCreate(
            friendly_name="Lab Workstation",
            rustdesk_id="222222222",
            hostname="lab-workstation",
            local_ip="10.10.10.10",
            operating_system="Ubuntu 20.04",
            username="lab-user",
            location="Research Lab",
            notes="For experimental setups",
            tags="lab,ubuntu,experimental"
        )
    ]
    
    try:
        # Create each sample computer
        for computer_data in sample_computers:
            try:
                create_computer(db, computer_data)
            except IntegrityError:
                # Skip if rustdesk_id already exists
                print(f"Skipping computer with rustdesk_id {computer_data.rustdesk_id} (already exists)")
                db.rollback()
    finally:
        # Close the database session
        db.close()

if __name__ == "__main__":
    seed_sample_data()
