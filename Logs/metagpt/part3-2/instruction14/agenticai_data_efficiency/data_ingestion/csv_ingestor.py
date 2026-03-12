import pandas as pd
from typing import List


class CSVIngestor:
    """
    Ingests data from one or more CSV files using pandas and returns a single DataFrame.
    """

    def __init__(self, csv_paths: List[str]):
        """
        csv_paths: list of CSV file paths to ingest.
        """
        if not isinstance(csv_paths, list):
            raise ValueError("csv_paths must be a list of file paths.")
        if not csv_paths:
            raise ValueError("csv_paths list is empty.")
        self.csv_paths = csv_paths

    def ingest(self) -> pd.DataFrame:
        """
        Reads all CSV files and concatenates them into a single DataFrame.
        Returns:
            pd.DataFrame: DataFrame containing the concatenated data from all CSV files.
        """
        dataframes = []
        for path in self.csv_paths:
            try:
                df = pd.read_csv(path)
            except Exception as e:
                raise RuntimeError(f"Failed to read CSV file '{path}': {e}")
            if df.empty:
                raise ValueError(f"CSV file '{path}' is empty.")
            dataframes.append(df)

        if not dataframes:
            raise ValueError("No data ingested from CSV files (all files empty or failed to read).")

        # Concatenate all DataFrames
        combined_df = pd.concat(dataframes, ignore_index=True)
        return combined_df