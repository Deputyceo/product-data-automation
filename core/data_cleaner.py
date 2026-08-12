import pandas as pd

from config import (
    COLUMN_DEPARTMENT,
    COLUMN_SUB_DEPARTMENT,
    COLUMN_CLASS,
    COLUMN_SUB_CLASS,
    COLUMN_ITEM_NAME,
    COLUMN_OH,
    DEFAULT_EXCLUDED_DEPARTMENTS,
    DEFAULT_EXCLUDED_DEPARTMENT_CODES,
    EXCLUDED_KEYWORDS,
)
from core.utils import load_ignored_departments, filter_empty_rows, sanitize_string


class DataCleaner:
    """Clean and filter product data using configurable rules."""

    def __init__(self):
        json_ignored = load_ignored_departments() or []
        combined_ignored = list(set(DEFAULT_EXCLUDED_DEPARTMENTS + json_ignored))
        self.ignored_departments = [dept.upper().strip() for dept in combined_ignored if dept]
        self.excluded_codes = [str(code).strip() for code in DEFAULT_EXCLUDED_DEPARTMENT_CODES if code]
        self.category_columns = [COLUMN_DEPARTMENT, COLUMN_SUB_DEPARTMENT, COLUMN_CLASS, COLUMN_SUB_CLASS]

    def remove_blank_on_hand(self, df):
        if df.empty:
            return df
        target = next((c for c in [COLUMN_OH, "201_OH", "201 OH", "201OH"] if c in df.columns), None)
        if not target:
            return df
        values = df[target].fillna("").astype(str).str.strip()
        keep = (values != "") & ~values.str.lower().isin(["nan", "none", "null"])
        return df[keep].copy()

    def remove_excluded_departments(self, df):
        if df.empty:
            return df
        cols = [c for c in self.category_columns if c in df.columns]
        if not cols:
            return df
        keep = pd.Series(True, index=df.index)
        for col in cols:
            values = df[col].fillna("").astype(str).str.upper().str.strip()
            for ignored in self.ignored_departments:
                keep &= ~values.str.contains(ignored, regex=False)
            for code in self.excluded_codes:
                keep &= ~(values.str.startswith(code) | values.str.contains(r'^\b' + code + r'\b', regex=True))
        return df[keep].copy()

    def remove_excluded_keywords(self, df, item_col=COLUMN_ITEM_NAME):
        if df.empty or item_col not in df.columns:
            return df
        names = df[item_col].apply(lambda x: sanitize_string(str(x)).upper())
        keep = pd.Series(True, index=df.index)
        for keyword in EXCLUDED_KEYWORDS:
            keep &= ~names.str.contains(keyword.upper(), regex=False)
        return df[keep].copy()

    def clean_new_items(self, df):
        if df.empty:
            return df
        cleaned = filter_empty_rows(df)
        cleaned = self.remove_blank_on_hand(cleaned)
        cleaned = self.remove_excluded_departments(cleaned)
        cleaned = self.remove_excluded_keywords(cleaned)
        return cleaned
