from pathlib import Path
from typing import Dict, Optional, Tuple, Union
import pandas as pd

from config import (
    COLUMN_DEPARTMENT,
    MAJOR_APPLIANCE_DEPARTMENT_TERMS,
    MAJOR_APPLIANCE_DEPARTMENT_CODES,
)
from core.comparator import DataComparator
from core.data_cleaner import DataCleaner
from core.excel_manager import ExcelManager
from core.logger import AppLogger
from core.validator import DataValidator


class AnalysisEngine:
    """Two-stage SKU reconciliation and product filtering engine."""

    def __init__(self):
        self.logger = AppLogger.get_logger("AnalysisEngine")
        self.cleaner = DataCleaner()
        self.major_appliances_df = pd.DataFrame()

    def run_stage_1_matching(
        self,
        new_items_path: Union[str, Path],
        product_bible_path: Union[str, Path],
        tracker_path: Union[str, Path],
        uploaded_skus_path: Optional[Union[str, Path]] = None,
    ) -> Tuple[bool, Union[pd.DataFrame, str], Dict[str, int]]:
        """Return the pure SKU difference. No Stage 2 filtering is applied."""
        metrics = {
            "total_raw_items": 0,
            "after_bible_match": 0,
            "after_tracker_match": 0,
            "after_uploaded_match": 0,
            "unmatched_difference_count": 0,
        }
        try:
            df_new = ExcelManager.read_file(new_items_path)
            df_bible = ExcelManager.read_file(product_bible_path)
            df_tracker = ExcelManager.read_file(tracker_path)
            df_uploaded = pd.DataFrame()
            if uploaded_skus_path and Path(uploaded_skus_path).exists():
                df_uploaded = ExcelManager.read_file(uploaded_skus_path)

            df_new_raw = df_new.copy(deep=True)
            metrics["total_raw_items"] = len(df_new_raw)

            valid, msg = DataValidator.validate_new_items(df_new_raw.copy(deep=True))
            if not valid:
                return False, msg, metrics
            valid, msg = DataValidator.validate_product_bible(df_bible.copy(deep=True))
            if not valid:
                return False, msg, metrics
            valid, msg = DataValidator.validate_tracker(df_tracker.copy(deep=True))
            if not valid:
                return False, msg, metrics

            df_difference = DataComparator.get_missing_skus(df_new_raw, df_bible)
            metrics["after_bible_match"] = len(df_difference)
            df_difference = DataComparator.get_missing_skus(df_difference, df_tracker)
            metrics["after_tracker_match"] = len(df_difference)

            if not df_uploaded.empty:
                df_difference = DataComparator.get_missing_skus(df_difference, df_uploaded)
                metrics["after_uploaded_match"] = len(df_difference)

            df_raw_difference = df_difference.copy(deep=True)
            metrics["unmatched_difference_count"] = len(df_raw_difference)
            self.logger.info(f"Stage 1 Complete - raw SKU difference: {len(df_raw_difference)} items.")
            return True, df_raw_difference, metrics
        except Exception as e:
            error_msg = f"Stage 1 failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return False, error_msg, metrics

    def _separate_major_appliances(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Separate Major Appliances using configurable department terms/codes."""
        if df.empty:
            return df.copy(), pd.DataFrame(columns=df.columns)

        department_column = next(
            (c for c in [COLUMN_DEPARTMENT, "DEPARTMENT", "Department", "department"] if c in df.columns),
            None,
        )
        if department_column is None:
            self.logger.warning("Department column not found; Major Appliances separation skipped.")
            return df.copy(), pd.DataFrame(columns=df.columns)

        values = df[department_column].fillna("").astype(str).str.strip().str.upper()
        mask = pd.Series(False, index=df.index)

        for term in MAJOR_APPLIANCE_DEPARTMENT_TERMS:
            if term:
                mask |= values.str.contains(str(term).upper(), regex=False, na=False)

        for code in MAJOR_APPLIANCE_DEPARTMENT_CODES:
            code = str(code).strip()
            if code:
                mask |= values.str.match(r"^" + code + r"\s*-\s*", na=False)

        major_df = df[mask].copy()
        remaining_df = df[~mask].copy()
        self.logger.info(f"Major Appliances detected: {len(major_df)}")
        return remaining_df, major_df

    def run_stage_2_elimination(self, df_difference: pd.DataFrame) -> Tuple[bool, pd.DataFrame, Dict[str, int]]:
        """Separate Major Appliances, then apply configured Stage 2 filters."""
        metrics = {
            "input_difference_items": len(df_difference),
            "major_appliances": 0,
            "items_sent_to_filter": 0,
            "final_photoshoot_items": 0,
            "eliminated_items": 0,
        }
        try:
            self.major_appliances_df = pd.DataFrame(columns=df_difference.columns)
            df_for_filtering, self.major_appliances_df = self._separate_major_appliances(df_difference)
            metrics["major_appliances"] = len(self.major_appliances_df)
            metrics["items_sent_to_filter"] = len(df_for_filtering)

            df_final = self.cleaner.clean_new_items(df_for_filtering)
            metrics["final_photoshoot_items"] = len(df_final)
            metrics["eliminated_items"] = len(df_for_filtering) - len(df_final)
            self.logger.info(f"Stage 2 Complete: {len(df_final)} final products; {len(self.major_appliances_df)} Major Appliances separated.")
            return True, df_final, metrics
        except Exception as e:
            error_msg = f"Stage 2 failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.major_appliances_df = pd.DataFrame()
            return False, pd.DataFrame(), metrics
