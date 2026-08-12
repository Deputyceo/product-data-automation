import json
from pathlib import Path
from typing import List, Any
import pandas as pd

from config import IGNORED_DEPARTMENTS_FILE, DEFAULT_EXCLUDED_DEPARTMENTS


def load_ignored_departments() -> List[str]:
    """Load configurable ignored departments, falling back to defaults."""
    if IGNORED_DEPARTMENTS_FILE.exists():
        try:
            with open(IGNORED_DEPARTMENTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return [str(item).strip().upper() for item in data]
        except Exception as e:
            print(f"Warning: Failed to load {IGNORED_DEPARTMENTS_FILE}. Using defaults. Error: {e}")
    return [dept.upper() for dept in DEFAULT_EXCLUDED_DEPARTMENTS]


def sanitize_string(value: Any) -> str:
    """Convert an input value to a normalized string."""
    if pd.isna(value) or value is None:
        return ""
    val_str = str(value).strip()
    if val_str.endswith(".0"):
        val_str = val_str[:-2]
    return val_str


def clean_sku(sku_value: Any) -> str:
    """Normalize SKU values for reliable comparison."""
    clean_val = sanitize_string(sku_value)
    return clean_val.zfill(6) if clean_val.isdigit() and len(clean_val) < 6 else clean_val


def clean_barcode(barcode_value: Any) -> str:
    """Normalize barcode strings."""
    return sanitize_string(barcode_value)


def filter_empty_rows(df: pd.DataFrame, subset_cols: List[str] = None) -> pd.DataFrame:
    """Remove rows where identifying fields are completely blank."""
    if subset_cols:
        return df.dropna(subset=subset_cols, how="all").copy()
    return df.dropna(how="all").copy()
