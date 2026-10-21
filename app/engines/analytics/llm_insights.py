from app.schemas.insights import InsightReport
from app.services.gemini_client import generate_structured_output


def generate_insights(report: dict) -> InsightReport:
    prompt = f"""
You are a cautious market research analyst.

Analyze only the response data supplied below.

Rules:
- Never invent numbers, quotes, trends, or respondent opinions.
- Each insight must cite specific evidence from the supplied counts.
- Distinguish observed results from interpretations.
- State limitations when the sample is small or incomplete.
- If the data is insufficient for a conclusion, say so.
- Do not claim statistical significance without a suitable statistical test.
- Use dimension_coverage to identify research dimensions with low coverage
  or unmet targets, when this data is available.
- Treat target_attainment as a ratio between 0 and 1.
- Do not confuse achieved coverage with customer interest or purchase intent.
- Treat target_gap as a coverage gap, not a market-demand gap.
- If dimension_coverage is missing or empty, do not infer dimension-level results.

Response data:
{report}
"""

    result = generate_structured_output(prompt, InsightReport)

    if result.session_id != report["session_id"]:
        raise ValueError("Insight report returned an incorrect session ID.")

    if result.respondent_count != report["respondent_count"]:
        raise ValueError("Insight report returned an incorrect respondent count.")

    return result