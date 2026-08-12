from typing import List, Tuple
import pandas as pd

from config import (
    REQUIRED_NEW_ITEMS_COLUMNS,
    REQUIRED_PRODUCT_BIBLE_COLUMNS,
    REQUIRED_TRACKER_COLUMNS,
)


class DataValidator:
    """Validate input schemas before processing."""

    @staticmethod
    def validate_columns(df: pd.DataFrame, required_columns: List[str], dataset_name: str = "Dataset") -> Tuple[bool, List[str]]:
        if df.empty:
            return False, ["DataFrame is empty"]

        existing_cols = [str(col).strip() for col in df.columns]
        missing = [col for col in required_columns if col not in existing_cols]
        if missing:
            return False, missing
        return True, []

    @staticmethod
    def validate_new_items(df: pd.DataFrame) -> Tuple[bool, str]:
        is_valid, missing = DataValidator.validate_columns(df, REQUIRED_NEW_ITEMS_COLUMNS, "New Items")
        if not is_valid:
            return False, f"New Items file is missing required columns: {', '.join(missing)}"
        return True, "Valid"

    @staticmethod
    def validate_product_bible(df: pd.DataFrame) -> Tuple[bool, str]:
        is_valid, missing = DataValidator.validate_columns(df, REQUIRED_PRODUCT_BIBLE_COLUMNS, "Product Bible")
        if not is_valid:
            return False, f"Product Bible file is missing required columns: {', '.join(missing)}"
        return True, "Valid"

    @staticmethod
    def validate_tracker(df: pd.DataFrame) -> Tuple[bool, str]:
        is_valid, missing = DataValidator.validate_columns(df, REQUIRED_TRACKER_COLUMNS, "Content Tracker")
        if not is_valid:
            return False, f"Tracker file is missing required columns: {', '.join(missing)}"
        return True, "Valid"
