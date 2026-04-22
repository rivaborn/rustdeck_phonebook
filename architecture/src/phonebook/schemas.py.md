# src/phonebook/schemas.py

## Purpose
Defines Pydantic data models for creating, updating, and retrieving computer entries in the phonebook application, including validation rules and data formatting.

## Responsibilities
- Validate and sanitize input data for computer entries
- Ensure data integrity through field-level validation
- Format and normalize text fields (whitespace stripping)
- Provide output schema for computer records with timestamps

## Key Types
- ComputerCreate (Class): Data model for creating new computer entries with validation
- ComputerUpdate (Class): Data model for updating existing computer entries with validation
- ComputerOut (Class): Data model for outputting computer records with database timestamps

## Key Functions
### casual_greeting
- Purpose: Returns a formatted welcome message for a given name
- Calls: None

## Globals
- None

## Dependencies
- pydantic.BaseModel, Field, validator
- typing.Optional, List
- ipaddress
- phonebook.models.Computer
