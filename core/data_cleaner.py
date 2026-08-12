from typing import List
import pandas as pd
import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import (
    COLUMN_DEPARTMENT,
    COLUMN_SUB_DEPARTMENT,
    COLUMN_CLASS,
    COLUMN_SUB_CLASS,
    COLUMN_ITEM_NAME,
    COLUMN_OH,
    DEFAULT_EXCLUDED_DEPARTMENTS,
    EXCLUDED_KEYWORDS,
)
from core.utils import load_ignored_departments, filter_empty_rows, sanitize_string


class DataCleaner:
    """Cleans and filters DataFrames according to configurable business rules."""

    def __init__(self):
        json_ignored = load_ignored_departments() or []
        combined_ignored = list(set(DEFAULT_EXCLUDED_DEPARTMENTS + json_ignored))
        self.ignored_departments = [dept.upper().strip() for dept in combined_ignored if dept]
        self.excluded_codes = ["403", "404", "506", "207", "504"]
        self.category_columns = [
            COLUMN_DEPARTMENT,
            COLUMN_SUB_DEPARTMENT,
            COLUMN_CLASS,
            COLUMN_SUB_CLASS,
        ]

    def remove_blank_on_hand(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove rows where the configured 201 OH field is blank."""
        if df.empty:
            return df

        target_oh_col = None
        for col in [COLUMN_OH, "201_OH", "201 OH", "201OH"]:
            if col in df.columns:
                target_oh_col = col
                break

        if not target_oh_col:
            return df

        oh_series = df[target_oh_col].fillna("").astype(str).str.strip()
        keep_mask = (
            (oh_series != "")
            & (oh_series.str.lower() != "nan")
            & (oh_series.str.lower() != "none")
            & (oh_series.str.lower() != "null")
        )
        return df[keep_mask].copy()

    def remove_excluded_departments(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove rows matching configured departments/codes in category columns."""
        if df.empty:
            return df

        cols_to_check = [col for col in self.category_columns if col in df.columns]
        if not cols_to_check:
            return df

        keep_mask = pd.Series(True, index=df.index)

        for col in cols_to_check:
            raw_series = df[col].fillna("").astype(str).str.upper().str.strip()
            for ignored in self.ignored_departments:
                keep_mask &= ~raw_series.str.contains(ignored, regex=False)
            for code in self.excluded_codes:
                code_matches = (
                    raw_series.str.startswith(code)
                    | raw_series.str.contains(r'^\b' + code + r'\b', regex=True)
                )
                keep_mask &= ~code_matches

        return df[keep_mask].copy()

    def remove_excluded_keywords(self, df: pd.DataFrame, item_col: str = COLUMN_ITEM_NAME) -> pd.DataFrame:
        """Remove rows whose description contains configured excluded keywords."""
        if df.empty or item_col not in df.columns:
            return df

        item_names = df[item_col].apply(lambda x: sanitize_string(str(x)).upper())
        keep_mask = pd.Series(True, index=df.index)
        for kw in EXCLUDED_KEYWORDS:
            keep_mask &= ~item_names.str.contains(kw.upper(), regex=False)
        return df[keep_mask].copy()

    def clean_new_items(self, df: pd.DataFrame) -> pd.DataFrame:
        """Run the full Stage 2 filtering pipeline."""
        if df.empty:
            return df

        df_cleaned = filter_empty_rows(df)
        df_cleaned = self.remove_blank_on_hand(df_cleaned)
        df_cleaned = self.remove_excluded_departments(df_cleaned)
        df_cleaned = self.remove_excluded_keywords(df_cleaned)
        return df_cleaned
