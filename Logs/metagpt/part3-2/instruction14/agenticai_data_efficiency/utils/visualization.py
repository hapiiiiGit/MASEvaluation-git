import os
from typing import List, Dict
import matplotlib.pyplot as plt
import seaborn as sns

class Visualization:
    """
    Generates charts and visualizations from analysis results using matplotlib/seaborn.
    Saves images and returns their file paths.
    """

    def __init__(self, output_dir: str = "output/visualizations"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_charts(self, analysis_results: Dict) -> List[str]:
        """
        Generates charts based on analysis results and saves them as image files.

        Args:
            analysis_results (Dict): Results from the efficiency analysis.

        Returns:
            List[str]: List of file paths to the generated chart images.
        """
        chart_paths = []

        # Example 1: Bottleneck Impact Bar Chart
        bottlenecks = analysis_results.get("bottlenecks", [])
        if bottlenecks:
            desc = [b.get("description", f"Bottleneck {i+1}") for i, b in enumerate(bottlenecks)]
            impact = [b.get("impact", 0) for b in bottlenecks]
            plt.figure(figsize=(10, 6))
            sns.barplot(x=impact, y=desc, palette="Reds_r")
            plt.xlabel("Impact")
            plt.ylabel("Bottleneck Description")
            plt.title("Bottleneck Impact Analysis")
            chart_path = os.path.join(self.output_dir, "bottleneck_impact.png")
            plt.tight_layout()
            plt.savefig(chart_path)
            plt.close()
            chart_paths.append(chart_path)

        # Example 2: Efficiency Gap Metrics Bar Chart
        metrics = analysis_results.get("metrics", {})
        if metrics:
            metric_names = []
            gaps = []
            for name, info in metrics.items():
                metric_names.append(name)
                gaps.append(info.get("gap", 0))
            plt.figure(figsize=(10, 6))
            sns.barplot(x=metric_names, y=gaps, palette="Blues")
            plt.xlabel("Metric")
            plt.ylabel("Gap")
            plt.title("Efficiency Gap Metrics")
            plt.xticks(rotation=45, ha="right")
            chart_path = os.path.join(self.output_dir, "efficiency_gap_metrics.png")
            plt.tight_layout()
            plt.savefig(chart_path)
            plt.close()
            chart_paths.append(chart_path)

        # Example 3: Recommendations Pie Chart (by expected impact, if available)
        recommendations = analysis_results.get("recommendations", [])
        impacts = [rec.get("impact", None) for rec in recommendations if rec.get("impact", None) is not None]
        titles = [rec.get("title", f"Rec {i+1}") for i, rec in enumerate(recommendations) if rec.get("impact", None) is not None]
        if impacts and titles:
            plt.figure(figsize=(8, 8))
            plt.pie(impacts, labels=titles, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("pastel"))
            plt.title("Recommendations by Expected Impact")
            chart_path = os.path.join(self.output_dir, "recommendations_impact_pie.png")
            plt.tight_layout()
            plt.savefig(chart_path)
            plt.close()
            chart_paths.append(chart_path)

        # If AgenticAi returned its own visualizations, copy their paths
        agenticai_visuals = analysis_results.get("visualizations", [])
        for vpath in agenticai_visuals:
            if isinstance(vpath, str) and os.path.exists(vpath):
                chart_paths.append(vpath)

        return chart_paths