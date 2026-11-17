import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
WORKSPACE_DIR = BASE_DIR.parent

STORAGE_DIR = BASE_DIR / "storage"
UPLOAD_DIR = STORAGE_DIR / "uploads"
OUTPUT_DIR = STORAGE_DIR / "outputs"
HIGHLIGHT_DIR = STORAGE_DIR / "highlights"

DB_PATH = STORAGE_DIR / "egoweave.db"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
HIGHLIGHT_DIR.mkdir(parents=True, exist_ok=True)

TEAM_ID = "T07"
MAX_UPLOAD_SIZE_MB = 1024
DEFAULT_TARGET_BUDGET_RATIO = 0.145

