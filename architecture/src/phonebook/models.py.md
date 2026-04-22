# src/phonebook/models.py

## Purpose
Defines SQLAlchemy ORM models for storing computer inventory data with timestamp tracking.

## Responsibilities
- Define database schema for computer inventory records
- Manage computer metadata including identifiers, system info, and timestamps
- Provide ORM mapping for SQLite persistence
- Handle automatic timestamp creation and updates
- Support unique constraint on rustdesk_id field

## Key Types
- Computer (Class): Represents a computer inventory record with all system metadata

## Key Functions
None

## Globals
- Base (declarative_base): SQLAlchemy base class for model inheritance
- Computer (Class): Main database model class

## Dependencies
- sqlalchemy.Column, Integer, String, DateTime
- sqlalchemy.ext.declarative.declarative_base
- datetime.datetime.utcnow
