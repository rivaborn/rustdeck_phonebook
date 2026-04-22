# Suggested Commands for Development

## Running the Application
- `python src/phonebook/main.py` - Run the main application
- `uvicorn src.phonebook.main:app --reload` - Run with uvicorn for development

## Testing
- `pytest` - Run all tests
- `pytest tests/` - Run tests in tests directory
- `python -m unittest` - Run unittests

## Formatting and Linting
- `black .` - Format code with Black
- `flake8 .` - Lint code with Flake8
- `pylint src/` - Lint code with Pylint

## Git Operations
- `git status` - Show working tree status
- `git add .` - Add all changes
- `git commit -m "message"` - Commit changes
- `git push` - Push to remote

## Project Navigation
- `ls` - List directory contents
- `cd src/phonebook` - Change to phonebook directory
- `find . -name "*.py" | head -20` - Find Python files

## Database Operations
- `python src/phonebook/database.py` - Database setup/operations