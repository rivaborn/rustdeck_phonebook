# src/phonebook/routes/export.py

## Purpose
Provides API endpoints for exporting computer records in JSON and CSV formats from the phonebook database.

## Responsibilities
- Handle JSON export of all computer records via HTTP endpoint
- Handle CSV export of all computer records via HTTP endpoint
- Manage database session lifecycle for export operations
- Serialize database records using Pydantic schemas
- Return properly formatted HTTP responses with appropriate content types

## Key Types
- ComputerOut (Pydantic model): Schema for serializing computer records

## Key Functions
### export_json
- Purpose: Exports all computer records as a JSON array response
- Calls: get_db, get_all_computers, ComputerOut.model_validate, JSONResponse

### export_csv
- Purpose: Exports all computer records as a CSV-formatted streaming response
- Calls: get_db, get_all_computers, ComputerOut.model_validate, csv.DictWriter, StreamingResponse

## Globals
None

## Dependencies
- fastapi.Request, HTTPException, JSONResponse, StreamingResponse
- phonebook.database.get_db
- phonebook.crud.get_all_computers
- phonebook.schemas.ComputerOut
- typing.List
- io.StringIO
- csv
