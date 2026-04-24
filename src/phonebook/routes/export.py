"""
Module for exporting computer records in JSON and CSV formats.
"""
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from typing import List
from io import StringIO
import csv

from ..database import get_db
from ..crud import get_all_computers
from ..schemas import ComputerOut

router = APIRouter()

def export_json(request: Request) -> JSONResponse:
    """
    Export all computer records as JSON.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        JSONResponse containing array of all computer records
        
    Raises:
        HTTPException: 500 Internal Server Error if database operation fails
    """
    # Acquire database session via get_db dependency
    db = next(get_db())
    
    try:
        # Fetch all computers using get_all_computers(db)
        computers = get_all_computers(db)
        
        # Serialize computers to JSON using ComputerOut model
        # Return JSONResponse with serialized data
        return JSONResponse(content=[ComputerOut.model_validate(computer).model_dump() for computer in computers])
        
    except Exception as e:
        # Handle any database or serialization errors by returning 500 status
        raise HTTPException(status_code=500, detail="Internal server error during JSON export")
    finally:
        db.close()

def export_csv(request: Request) -> StreamingResponse:
    """
    Export all computer records as CSV.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        StreamingResponse with CSV data and proper headers
        
    Raises:
        HTTPException: 500 Internal Server Error if database operation fails
    """
    # Acquire database session via get_db dependency
    db = next(get_db())
    
    try:
        # Fetch all computers using get_all_computers(db)
        computers = get_all_computers(db)
        
        # Create CSV writer with headers matching ComputerOut fields
        # Stream CSV rows using csv.DictWriter
        # Set Content-Disposition header to attachment with filename "phonebook.csv"
        # Return StreamingResponse with CSV data and text/csv content type
        
        # Prepare CSV data
        output = StringIO()
        if computers:
            # Get field names from ComputerOut model
            fieldnames = list(ComputerOut.model_fields.keys())
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write data rows
            for computer in computers:
                # Convert computer to dict using ComputerOut schema
                computer_dict = ComputerOut.model_validate(computer).model_dump()
                writer.writerow(computer_dict)
        else:
            # Even if no data, write header row
            fieldnames = list(ComputerOut.model_fields.keys())
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
        
        # Return StreamingResponse with CSV data and text/csv content type
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=phonebook.csv"}
        )
        
    except Exception as e:
        # Handle any database or CSV generation errors by returning 500 status
        raise HTTPException(status_code=500, detail="Internal server error during CSV export")
    finally:
        db.close()

# Add routes to the router
router.get("/export/json")(export_json)
router.get("/export/csv")(export_csv)
