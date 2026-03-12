import pandas as pd
from typing import List


class DataUnifier:
    """
    Unifies multiple pandas DataFrames and preprocesses the unified data for analysis.
    """

    def __init__(self):
        pass

    def unify(self, dfs: List[pd.DataFrame]) -> pd.DataFrame:
        """
        Unifies a list of DataFrames into a single DataFrame.
        Handles column alignment and merges on common columns if possible.
        If columns do not match, performs an outer join on all columns.

        Args:
            dfs (List[pd.DataFrame]): List of DataFrames to unify.

        Returns:
            pd.DataFrame: Unified DataFrame.
        """
        if not dfs or not all(isinstance(df, pd.DataFrame) for df in dfs):
            raise ValueError("Input must be a list of pandas DataFrames.")

        # If all DataFrames have the same columns, concatenate directly
        columns_sets = [set(df.columns) for df in dfs]
        if all(columns_sets[0] == cols for cols in columns_sets):
            unified_df = pd.concat(dfs, ignore_index=True)
        else:
            # Outer join on all columns
            unified_df = pd.concat(dfs, ignore_index=True, sort=False)

        if unified_df.empty:
            raise ValueError("Unified DataFrame is empty after concatenation.")

        return unified_df

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocesses the unified DataFrame for analysis.
        Typical steps: drop duplicates, handle missing values, standardize column names, and convert data types.

        Args:
            df (pd.DataFrame): Unified DataFrame.

        Returns:
            pd.DataFrame: Preprocessed DataFrame.
        """
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame.")

        # Standardize column names: lowercase, replace spaces with underscores
        df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]

        # Drop duplicate rows
        df = df.drop_duplicates()

        # Handle missing values: fill numeric columns with median, categorical with mode
        for col in df.columns:
            if df[col].dtype.kind in "biufc":  # Numeric columns
                median = df[col].median()
                df[col] = df[col].fillna(median)
            else:  # Categorical columns
                mode = df[col].mode()
                if not mode.empty:
                    df[col] = df[col].fillna(mode[0])
                else:
                    df[col] = df[col].fillna("unknown")

        # Convert object columns that look like dates to datetime
        for col in df.select_dtypes(include=["object"]).columns:
            try:
                df[col] = pd.to_datetime(df[col], errors="ignore")
            except Exception:
                pass

        # Optionally, remove columns with all missing values
        df = df.dropna(axis=1, how="all")

        if df.empty:
            raise ValueError("Preprocessed DataFrame is empty.")

        return df