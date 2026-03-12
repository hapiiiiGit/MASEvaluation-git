import os
from typing import Dict
from jinja2 import Environment, FileSystemLoader, select_autoescape

class ReportGenerator:
    """
    Generates a Markdown report from analysis results using a Jinja2 template.
    """

    def __init__(self, template_path: str):
        """
        Initializes the ReportGenerator with the path to the Jinja2 template.
        Args:
            template_path (str): Path to the Markdown template file.
        """
        self.template_path = template_path
        self.env = Environment(
            loader=FileSystemLoader(os.path.dirname(template_path)),
            autoescape=select_autoescape(['md'])
        )
        self.template = self.env.get_template(os.path.basename(template_path))

    def generate(self, analysis_results: Dict, output_path: str) -> None:
        """
        Renders the report using the template and writes it to the output path.
        Args:
            analysis_results (Dict): Results from the efficiency analysis.
            output_path (str): Path to write the rendered report.
        """
        # Prepare context for the template
        context = {
            "bottlenecks": analysis_results.get("bottlenecks", []),
            "efficiency_gaps": analysis_results.get("efficiency_gaps", []),
            "recommendations": analysis_results.get("recommendations", []),
            "metrics": analysis_results.get("metrics", {}),
            "visualizations": analysis_results.get("visualizations", []),
            "raw_agenticai_output": analysis_results.get("raw_agenticai_output", {}),
        }

        rendered_report = self.template.render(**context)

        # Write the rendered report to the output file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered_report)