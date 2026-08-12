from datetime import datetime
from pathlib import Path
from typing import Union, Dict, Optional

import pandas as pd

from config import OUTPUT_DIR
from core.excel_manager import ExcelManager
from core.logger import AppLogger


class DataExporter:
    """Export Stage 1 and Stage 2 results to timestamped Excel reports."""

    def __init__(self, output_dir: Optional[Union[str, Path]] = None):
        self.output_dir = Path(output_dir) if output_dir else OUTPUT_DIR
        self.logger = AppLogger.get_logger("DataExporter")

    def _generate_timestamped_filename(self, base_name: str, extension: str = ".xlsx") -> Path:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        ext = extension if extension.startswith(".") else f".{extension}"
        return self.output_dir / f"{base_name}_{timestamp}{ext}"

    def export_photoshoot_items(self, df: pd.DataFrame, filename_prefix: str = "New_Items_For_Photoshoot", file_format: str = "xlsx") -> Path:
        """Export a single DataFrame, used for the raw Stage 1 report."""
        if df.empty:
            self.logger.warning("Attempted to export an empty DataFrame.")

        export_path = self._generate_timestamped_filename(filename_prefix, file_format)
        try:
            ExcelManager.write_file(df, export_path)
            self.logger.info(f"Successfully exported {len(df)} rows to: {export_path}")
            return export_path
        except Exception as e:
            self.logger.error(f"Failed to export photoshoot items: {str(e)}")
            raise

    def export_stage_2_results(self, final_df: pd.DataFrame, major_appliances_df: pd.DataFrame, filename_prefix: str = "Stage2_Final_Photoshoot_List") -> Path:
        """Export Stage 2 into one workbook with Final Products and MAJOR APPLIANCES sheets."""
        final_df = final_df if final_df is not None else pd.DataFrame()
        major_appliances_df = major_appliances_df if major_appliances_df is not None else pd.DataFrame()
        export_path = self._generate_timestamped_filename(filename_prefix, ".xlsx")

        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            with pd.ExcelWriter(export_path, engine="openpyxl") as writer:
                final_df.to_excel(writer, sheet_name="Final Products", index=False)
                major_appliances_df.to_excel(writer, sheet_name="MAJOR APPLIANCES", index=False)

            self.logger.info(f"Stage 2 workbook exported successfully: {export_path}")
            self.logger.info(f"Final Products: {len(final_df)}")
            self.logger.info(f"Major Appliances: {len(major_appliances_df)}")
            return export_path
        except Exception as e:
            self.logger.error(f"Failed to export Stage 2 workbook: {str(e)}")
            raise

    def export_summary_report(self, metrics: Dict[str, int], filename_prefix: str = "Pipeline_Summary") -> Path:
        """Export pipeline metrics as a summary workbook."""
        df_summary = pd.DataFrame(list(metrics.items()), columns=["Metric", "Value"])
        export_path = self._generate_timestamped_filename(filename_prefix, "xlsx")
        ExcelManager.write_file(df_summary, export_path, sheet_name="Summary")
        self.logger.info(f"Summary report written to: {export_path}")
        return export_path
