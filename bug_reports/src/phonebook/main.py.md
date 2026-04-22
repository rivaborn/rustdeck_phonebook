# src/phonebook/main.py

## Findings

### Missing Error Handling in Database Initialization [HIGH]
- **Where:** `lifespan()` ~line 25
- **Issue:** The `init_db()` call in the lifespan context manager has no error handling.
- **Impact:** If database initialization fails, the application will start with a broken database state, potentially causing crashes or data corruption when routes try to access the database.
- **Fix:** Wrap `init_db()` in a try-except block and log/raise the exception to prevent the app from starting in a bad state.

### Incorrect Lifespan Assignment [MEDIUM]
- **Where:** `app.router.lifespan_context = lifespan` ~line 34
- **Issue:** The lifespan is assigned directly to `app.router.lifespan_context` instead of using `app.router.lifespan_context = lifespan` or FastAPI's built-in `lifespan` parameter.
- **Impact:** This may not properly register the lifespan context manager with FastAPI, leading to missing cleanup or initialization logic during app startup/shutdown.
- **Fix:** Use `app = FastAPI(lifespan=lifespan)` when creating the app instance instead of manually assigning it to the router.

### Hardcoded Paths in Mount and Template Directories [LOW]
- **Where:** `app.mount("/static", "src/phonebook/static/", name="static")` ~line 19, `templates = Jinja2Templates(directory="src/phonebook/templates/")` ~line 22
- **Issue:** The paths for static files and templates are hardcoded as relative paths.
- **Impact:** This could cause issues if the application is run from a different working directory or deployed in a containerized environment.
- **Fix:** Use absolute paths or `os.path.join()` with `__file__` to ensure correct resolution regardless of working directory.

## Verdict

ISSUES FOUND
