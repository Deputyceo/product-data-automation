from typing import List
import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import COLUMN_SKU
from core.utils import clean_sku


class DataComparator:
    """Compare SKU values between source and reference datasets."""

    @staticmethod
    def get_missing_skus(source_df: pd.DataFrame, reference_df: pd.DataFrame, sku_col: str = COLUMN_SKU) -> pd.DataFrame:
        """Return source rows whose SKUs do not exist in the reference."""
        if source_df.empty:
            return pd.DataFrame()
        if reference_df.empty:
            return source_df.copy()

        source_skus = source_df[sku_col].apply(clean_sku)
        reference_skus = set(reference_df[sku_col].apply(clean_sku))
        missing_mask = ~source_skus.isin(reference_skus)
        return source_df[missing_mask].copy()

    @staticmethod
    def get_matching_skus(source_df: pd.DataFrame, reference_df: pd.DataFrame, sku_col: str = COLUMN_SKU) -> pd.DataFrame:
        """Return source rows whose SKUs exist in the reference."""
        if source_df.empty or reference_df.empty:
            return pd.DataFrame()

        source_skus = source_df[sku_col].apply(clean_sku)
        reference_skus = set(reference_df[sku_col].apply(clean_sku))
        matching_mask = source_skus.isin(reference_skus)
        return source_df[matching_mask].copy()

    @staticmethod
    def compare_multiple_references(source_df: pd.DataFrame, reference_dfs: List[pd.DataFrame], sku_col: str = COLUMN_SKU) -> pd.DataFrame:
        """Filter out SKUs present in any reference DataFrame."""
        filtered_df = source_df.copy()
        for ref_df in reference_dfs:
            if not ref_df.empty:
                filtered_df = DataComparator.get_missing_skus(filtered_df, ref_df, sku_col)
        return filtered_df
