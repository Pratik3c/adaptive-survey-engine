from app.schemas.project_insights import ProjectInsightReport
from app.services.gemini_client import generate_structured_output


def generate_project_insights(report: dict) -> ProjectInsightReport:
    prompt = f"""
You are a cautious market research analyst.

Analyze the aggregated survey results supplied below.

Rules:
- Use only the supplied data.
- Never invent percentages, counts, quotations, or trends.
- Every insight must cite specific evidence from the supplied question results,
  counts, or dimension coverage data.
- Distinguish observed data from interpretation.
- Mention sample-size, adaptive-question, and sampling limitations.
- Do not claim statistical significance or causation.
- If the data is insufficient, explicitly say so.
- Use dimension coverage to identify research dimensions with low coverage
  or unmet coverage targets, when this data is available.
- Treat target_attainment as a ratio between 0 and 1, not a percentage.
- Treat target_gap as a research coverage gap, not a market-demand gap.
- Do not confuse achieved coverage with customer interest or purchase intent.
- If dimension coverage data is missing or empty, do not infer
  dimension-level results.
- Dimension averages may cover only sessions with saved coverage records;
  mention this limitation when applicable.
- Do not interpret ineligible respondents as eligible customer feedback.
- Do not treat the number of sessions as a verified count of unique people.

Data:
{report}
"""

    result = generate_structured_output(prompt, ProjectInsightReport)

    if result.research_id != report["research_id"]:
        raise ValueError("Incorrect research ID in generated insights.")

    if result.respondent_count != report["eligible_sessions"]:
        raise ValueError("Incorrect respondent count in generated insights.")

    return result
