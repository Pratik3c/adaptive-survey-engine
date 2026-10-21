from app.db.models import (
    ResearchProject,
    SurveyRun,
    SurveyAnswer,
    SessionDimensionCoverage,
)
from app.engines.adaptive.selector import (
    calculate_coverage,
    calculate_target_attainment,
)


def update_session_coverage(db, session_id: int, survey):
    run = db.query(SurveyRun).filter(
        SurveyRun.id == session_id
    ).first()

    if run is None:
        raise ValueError(f"Session {session_id} not found")

    project = db.query(ResearchProject).filter(
        ResearchProject.id == run.project_id
    ).first()

    if project is None:
        raise ValueError(f"Research project for session {session_id} not found")

    dimensions = project.dimensions
    answers = (
        db.query(SurveyAnswer)
        .filter(SurveyAnswer.session_id == session_id)
        .all()
    )

    answered_ids = {answer.question_id for answer in answers}
    question_lookup = {
        question.question_id: question
        for question in survey.questions
    }

    coverage = {dimension.name: 0.0 for dimension in dimensions}

    # Ineligible respondents should not contribute research coverage.
    if run.status != "ineligible":
        for question_id in answered_ids:
            question = question_lookup.get(question_id)
            if question is None:
                continue

            for dimension_name, strength in question.dimension_mappings.items():
                if dimension_name in coverage:
                    coverage[dimension_name] = max(
                        coverage[dimension_name],
                        min(max(float(strength), 0.0), 1.0),
                    )

    # Reuse the project's existing weighting formulas.
    overall_coverage = calculate_coverage(dimensions, coverage)
    overall_attainment = calculate_target_attainment(dimensions, coverage)

    for dimension in dimensions:
        achieved = coverage[dimension.name]

        if dimension.target_coverage <= 0:
            attainment = 1.0
        else:
            attainment = min(
                achieved / dimension.target_coverage,
                1.0,
            )

        record = db.query(SessionDimensionCoverage).filter(
            SessionDimensionCoverage.session_id == session_id,
            SessionDimensionCoverage.dimension_id == dimension.id,
        ).first()

        if record is None:
            record = SessionDimensionCoverage(
                session_id=session_id,
                dimension_id=dimension.id,
            )
            db.add(record)

        record.achieved_coverage = round(achieved, 4)
        record.target_coverage = float(dimension.target_coverage)
        record.target_attainment = round(attainment, 4)

    db.flush()

    return {
        "weighted_coverage": round(overall_coverage, 4),
        "target_attainment": round(overall_attainment, 4),
        "dimension_coverage": coverage,
    }