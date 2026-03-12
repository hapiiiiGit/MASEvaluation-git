import yaml
import os

class Config:
    """
    Handles configuration loading for the AgenticAi data efficiency program.
    Loads PostgreSQL credentials, CSV file paths, and report format from a YAML config file.
    Provides accessors for each configuration item.
    """

    def __init__(self, config_path: str):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        with open(config_path, "r") as f:
            self._config = yaml.safe_load(f)

    def get_postgres_config(self) -> dict:
        """
        Returns PostgreSQL configuration as a dictionary.
        Expected keys: host, port, user, password, database, table, query (optional).
        """
        pg_config = self._config.get("postgres", {})
        required_keys = ["host", "port", "user", "password", "database", "table"]
        missing = [k for k in required_keys if k not in pg_config]
        if missing:
            raise ValueError(f"Missing PostgreSQL config keys: {missing}")
        return pg_config

    def get_csv_paths(self) -> list:
        """
        Returns a list of CSV file paths.
        """
        csv_paths = self._config.get("csv_files", [])
        if not isinstance(csv_paths, list):
            raise ValueError("csv_files must be a list of file paths.")
        for path in csv_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"CSV file not found: {path}")
        return csv_paths

    def get_report_format(self) -> str:
        """
        Returns the desired report format (markdown, pdf, html).
        Defaults to 'md' (Markdown).
        """
        fmt = self._config.get("report_format", "md").lower()
        valid_formats = ["md", "markdown", "pdf", "html"]
        if fmt not in valid_formats:
            raise ValueError(f"Invalid report format: {fmt}. Valid options: {valid_formats}")
        # Normalize to file extension
        if fmt in ["md", "markdown"]:
            return "md"
        return fmt

    def get(self, key: str, default=None):
        """
        Generic getter for config values.
        """
        return self._config.get(key, default)