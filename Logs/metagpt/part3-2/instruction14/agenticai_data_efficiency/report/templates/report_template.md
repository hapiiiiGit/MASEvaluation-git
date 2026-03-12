# Operational Efficiency Analysis Report

## Executive Summary

This report presents the results of an operational efficiency analysis performed using the AgenticAi framework. The analysis covers data ingested from PostgreSQL and CSV sources, identifying key bottlenecks, efficiency gaps, and providing actionable recommendations supported by relevant metrics and visualizations.

---

## Bottleneck Analysis

{% if bottlenecks %}
### Key Bottlenecks Identified

| # | Description | Impact | Location/Process |
|---|-------------|--------|------------------|
{% for bottleneck in bottlenecks %}
| {{ loop.index }} | {{ bottleneck.description }} | {{ bottleneck.impact }} | {{ bottleneck.location }} |
{% endfor %}
{% else %}
_No significant bottlenecks detected._
{% endif %}

---

## Efficiency Gap Metrics

{% if metrics %}
### Efficiency Metrics

| Metric | Value | Target | Gap | Notes |
|--------|-------|--------|-----|-------|
{% for metric_name, metric_info in metrics.items() %}
| {{ metric_name }} | {{ metric_info.value }} | {{ metric_info.target }} | {{ metric_info.gap }} | {{ metric_info.notes }} |
{% endfor %}
{% else %}
_No efficiency metrics available._
{% endif %}

---

## Recommendations

{% if recommendations %}
### Actionable Recommendations

{% for rec in recommendations %}
- **{{ rec.title }}**  
  {{ rec.detail }}
  {% if rec.impact %}_Expected Impact:_ {{ rec.impact }}{% endif %}
{% endfor %}
{% else %}
_No recommendations generated._
{% endif %}

---

## Visualizations

{% if visualizations %}
### Charts & Graphs

{% for chart_path in visualizations %}
![Visualization {{ loop.index }}]({{ chart_path }})
{% endfor %}
{% else %}
_No visualizations available._
{% endif %}

---

## Appendix

### Raw AgenticAi Output
