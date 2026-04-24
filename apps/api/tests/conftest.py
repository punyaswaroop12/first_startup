import os
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("AI_PROVIDER", "fake")

test_db = Path("test.db")
if test_db.exists():
    test_db.unlink()
