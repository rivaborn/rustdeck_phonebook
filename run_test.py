import sys
import os
sys.path.insert(0, os.path.abspath('.'))

try:
    from src.phonebook.main import app
    print("SUCCESS: Application imported correctly")
    print("App title:", app.title)
    print("App version:", app.version)
except Exception as e:
    print("ERROR:", str(e))
    import traceback
    traceback.print_exc()