from pathlib import Path
from typing import Union, Optional
import pandas as pd


class ExcelManager:
    """Centralized utility for safely reading and writing Excel/CSV files."""

    @staticmethod
    def read_file(file_path: Union[str, Path], sheet_name: Optional[Union[str, int]] = 0) -> pd.DataFrame:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        ext = path.suffix.lower()
        try:
            if ext in [".xlsx", ".xls"]:
                df = pd.read_excel(path, sheet_name=sheet_name, dtype=str)
            elif ext == ".csv":
                df = pd.read_csv(path, dtype=str)
            else:
                raise ValueError(f"Unsupported file format: {ext}. Expected .xlsx, .xls, or .csv")

            df.columns = [str(col).strip() for col in df.columns]
            return df
        except Exception as e:
            raise RuntimeError(f"Error reading file '{path.name}': {str(e)}")

    @staticmethod
    def write_file(df: pd.DataFrame, output_path: Union[str, Path], sheet_name: str = "Sheet1") -> bool:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        ext = path.suffix.lower()

        try:
            if ext in [".xlsx", ".xls"]:
                with pd.ExcelWriter(path, engine="openpyxl") as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            elif ext == ".csv":
                df.to_csv(path, index=False, encoding="utf-8-sig")
            else:
                raise ValueError(f"Unsupported export format: {ext}")
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to write file to '{path}': {str(e)}")
