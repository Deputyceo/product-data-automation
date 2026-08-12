from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"
SAMPLES_DIR = BASE_DIR / "samples"
ASSETS_DIR = BASE_DIR / "assets"

for directory in (OUTPUT_DIR, LOGS_DIR):
    directory.mkdir(parents=True, exist_ok=True)

IGNORED_DEPARTMENTS_FILE = DATA_DIR / "ignored_departments.json"

# Generic examples only. Replace these with your own rules locally.
DEFAULT_EXCLUDED_DEPARTMENTS = [
    "EXCLUDED CATEGORY EXAMPLE",
    "INTERNAL TEST CATEGORY",
]
DEFAULT_EXCLUDED_DEPARTMENT_CODES = []
EXCLUDED_KEYWORDS = ["EXAMPLE KEYWORD"]

# Major Appliance detection is configurable and intentionally contains
# no company-specific department code in the public project.
MAJOR_APPLIANCE_DEPARTMENT_TERMS = ["MAJOR APPLIANCES", "MAJORS APPLIANCES"]
MAJOR_APPLIANCE_DEPARTMENT_CODES = []

COLUMN_SKU = "SKU"
COLUMN_BARCODE = "Barcode"
COLUMN_DEPARTMENT = "DEPARTMENT"
COLUMN_SUB_DEPARTMENT = "SUBDEPARTMENT"
COLUMN_CLASS = "CLASS"
COLUMN_SUB_CLASS = "SUBCLASS"
COLUMN_ITEM_NAME = "DESCRIPTION"
COLUMN_OH = "201_OH"

REQUIRED_NEW_ITEMS_COLUMNS = [COLUMN_SKU, COLUMN_DEPARTMENT]
REQUIRED_PRODUCT_BIBLE_COLUMNS = [COLUMN_SKU]
REQUIRED_TRACKER_COLUMNS = [COLUMN_SKU]

LOG_FORMAT = "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
