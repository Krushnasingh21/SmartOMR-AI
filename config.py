
from pathlib import Path

# ==========================================
# 1. PROJECT INFORMATION
# ==========================================

PROJECT_NAME = "SmartOMR AI"
PROJECT_VERSION = "1.0.0"
APP_TITLE = "SmartOMR AI - OMR Scanning & Evaluation"


# ==========================================
# 2. PROJECT DIRECTORY
# ==========================================

BASE_DIR = Path(__file__).resolve().parent


# ==========================================
# 3. MAIN FOLDER PATHS
# ==========================================

SRC_DIR = BASE_DIR / "src"
PAGES_DIR = BASE_DIR / "pages"
TEMPLATES_DIR = BASE_DIR / "templates"
ML_DIR = BASE_DIR / "ml"
DATABASE_DIR = BASE_DIR / "database"
MODELS_DIR = BASE_DIR / "models"

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

UPLOAD_DIR = BASE_DIR / "uploads"
REPORT_DIR = BASE_DIR / "reports"
TEST_DIR = BASE_DIR / "tests"


# ==========================================
# 4. APPLICATION SETTINGS
# ==========================================

SUPPORTED_IMAGE_EXTENSIONS = [
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff"
]

MAX_UPLOAD_SIZE_MB = 10

DEFAULT_QUESTIONS = 100
DEFAULT_OPTIONS = ["A", "B", "C", "D"]


# ==========================================
# 5. DATABASE SETTINGS
# ==========================================

DATABASE_PATH = DATABASE_DIR / "smartomr.db"

DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"


# ==========================================
# 6. CREATE REQUIRED DIRECTORIES
# ==========================================

def create_required_directories():
    """Create project directories if they do not exist."""

    directories = [
        SRC_DIR,
        PAGES_DIR,
        TEMPLATES_DIR,
        ML_DIR,
        DATABASE_DIR,
        MODELS_DIR,
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        UPLOAD_DIR,
        REPORT_DIR,
        TEST_DIR
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    create_required_directories()
    print(f"{PROJECT_NAME} configuration loaded successfully!")
    print(f"Project location: {BASE_DIR}")
    print(f"Database location: {DATABASE_PATH}")
