# src/phonebook/crud.py

## Purpose
Provides database CRUD operations for Computer entities with search and timestamp management.

## Responsibilities
- Query all computers with ordered results
- Retrieve specific computers by ID
- Search computers across multiple fields using OR logic
- Create new computer records with timestamps
- Update existing computer records conditionally

## Key Types
- Computer (Class): Database model representing computer entities
- ComputerCreate (Class): Pydantic schema for creating computers
- ComputerUpdate (Class): Pydantic schema for updating computers

## Key Functions
### get_all_computers
- Purpose: Retrieve all computer records ordered by friendly name
- Calls: db.query(), order_by(), all()

### get_computer
- Purpose: Fetch a single computer by its ID
- Calls: db.query(), filter(), first()

### search_computers
- Purpose: Search computers across multiple fields using OR logic
- Calls: db.query(), or_(), ilike(), filter()

### create_computer
- Purpose: Create a new computer record with timestamps
- Calls: Computer(), db.add(), db.commit(), db.refresh()

### update_computer
- Purpose: Update computer fields conditionally skipping None values
- Calls: get_computer(), db.commit(), db.refresh()

### delete_computer
- Purpose: Remove a computer record by ID
- Calls: get_computer(), db.delete(), db.commit()

## Globals
None

## Dependencies
- phonebook.models.Computer
- phonebook.schemas.ComputerCreate
- phonebook.schemas.ComputerUpdate
- phonebook.database.Session
- sqlalchemy.exc.IntegrityError
- sqlalchemy.or_
- datetime.datetime
- pytz.UTC
