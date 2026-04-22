# src/phonebook/config.py

## Purpose
Defines application configuration settings using Pydantic and provides a cached settings instance for the phonebook application.

## Responsibilities
- Define typed configuration variables with defaults
- Load settings from environment file with fallback to defaults
- Provide cached access to configuration instance
- Support environment variable override for configuration

## Key Types
- Settings (BaseSettings): Configuration schema with typed fields and environment loading

## Key Functions
### get_settings
- Purpose: Returns cached Settings instance with parsed environment variables
- Calls: Settings()

## Globals
- None

## Dependencies
- pydantic_settings.BaseSettings
- pydantic_settings.SettingsConfigDict
- functools.lru_cache
