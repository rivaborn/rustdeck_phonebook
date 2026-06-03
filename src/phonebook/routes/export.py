"""
Module for exporting computer records in JSON and CSV formats.
"""
import csv
from io import StringIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session

from ..crud import get_all_computers
from ..database import get_db
from ..schemas import ComputerOut

router = APIRouter()


@router.get("/export/json")
def export_json(db: Session = Depends(get_db)) -> JSONResponse:
    """Export all computer records as a JSON array."""
    try:
        computers = get_all_computers(db)
        return JSONResponse(
            content=[ComputerOut.model_validate(computer).model_dump() for computer in computers]
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error during JSON export")


@router.get("/export/csv")
def export_csv(db: Session = Depends(get_db)) -> StreamingResponse:
    """Export all computer records as a CSV attachment."""
    try:
        computers = get_all_computers(db)

        output = StringIO()
        fieldnames = list(ComputerOut.model_fields.keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for computer in computers:
            writer.writerow(ComputerOut.model_validate(computer).model_dump())

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=phonebook.csv"},
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error during CSV export")
