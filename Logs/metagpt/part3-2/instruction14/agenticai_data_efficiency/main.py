import os
import sys

from config import Config
from data_ingestion.postgres_ingestor import PostgresIngestor
from data_ingestion.csv_ingestor import CSVIngestor
from data_ingestion.data_unifier import DataUnifier
from analysis.efficiency_analyzer import EfficiencyAnalyzer
from report.report_generator import ReportGenerator
from utils.visualization import Visualization

def main():
    # Load configuration
    config_path = os.environ.get("AGENTICAI_CONFIG_PATH", "config.yaml")
    config = Config(config_path)
    postgres_config = config.get_postgres_config()
    csv_paths = config.get_csv_paths()
    report_format = config.get_report_format()
    report_template_path = os.path.join("report", "templates", "report_template.md")
    report_output_path = os.path.join("output", f"efficiency_report.{report_format}")

    # Ingest data from PostgreSQL
    print("Ingesting data from PostgreSQL...")
    pg_ingestor = PostgresIngestor(postgres_config)
    pg_df = pg_ingestor.ingest()

    # Ingest data from CSV files
    print("Ingesting data from CSV files...")
    csv_ingestor = CSVIngestor(csv_paths)
    csv_df = csv_ingestor.ingest()

    # Unify and preprocess data
    print("Unifying and preprocessing data...")
    data_unifier = DataUnifier()
    unified_df = data_unifier.unify([pg_df, csv_df])
    preprocessed_df = data_unifier.preprocess(unified_df)

    # Analyze data for efficiency insights using AgenticAi APIs
    print("Analyzing data for efficiency insights...")
    try:
        from agenticai import AgenticAiClient
    except ImportError:
        print("Error: AgenticAi SDK is not installed. Please install it before running the program.")
        sys.exit(1)
    agenticai_client = AgenticAiClient()
    analyzer = EfficiencyAnalyzer(agenticai_client)
    analysis_results = analyzer.analyze(preprocessed_df)

    # Generate charts/visualizations
    print("Generating visualizations...")
    visualization = Visualization()
    chart_paths = visualization.generate_charts(analysis_results)

    # Generate report
    print("Generating report...")
    report_generator = ReportGenerator(report_template_path)
    # Ensure output directory exists
    os.makedirs(os.path.dirname(report_output_path), exist_ok=True)
    report_generator.generate(analysis_results, report_output_path)

    print(f"Report generated at: {report_output_path}")
    print("Done.")

if __name__ == "__main__":
    main()