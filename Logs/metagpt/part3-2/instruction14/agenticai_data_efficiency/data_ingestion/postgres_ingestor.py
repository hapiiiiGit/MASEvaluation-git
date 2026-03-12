import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from typing import Dict, Optional


class PostgresIngestor:
    """
    Ingests data from a PostgreSQL database using SQLAlchemy and returns a pandas DataFrame.
    """

    def __init__(self, db_config: Dict):
        """
        db_config: dict with keys:
            - host
            - port
            - user
            - password
            - database
            - table
            - query (optional)
        """
        self.db_config = db_config
        self.engine = self._create_engine()

    def _create_engine(self):
        url = URL.create(
            drivername="postgresql+psycopg2",
            username=self.db_config["user"],
            password=self.db_config["password"],
            host=self.db_config["host"],
            port=self.db_config["port"],
            database=self.db_config["database"],
        )
        return create_engine(url)

    def ingest(self) -> pd.DataFrame:
        """
        Ingests data from the specified PostgreSQL table or using a custom query.
        Returns:
            pd.DataFrame: DataFrame containing the ingested data.
        """
        query = self.db_config.get("query")
        table = self.db_config["table"]

        if query:
            sql = query
        else:
            sql = f"SELECT * FROM {table}"

        try:
            df = pd.read_sql(sql, self.engine)
        except Exception as e:
            raise RuntimeError(f"Failed to ingest data from PostgreSQL: {e}")

        if df.empty:
            raise ValueError("No data ingested from PostgreSQL (resulting DataFrame is empty).")

        return df