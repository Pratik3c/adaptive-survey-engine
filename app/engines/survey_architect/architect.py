from app.schemas.question import (
    AnswerOption,
    SurveyQuestion,
    SurveyBlueprint,
)


def build_survey(research_id: int, topic: str, dimensions: list) -> SurveyBlueprint:
    questions = []

    # Eligibility question
    questions.append(
        SurveyQuestion(
            question_id="Q001",
            text="Which age group do you belong to?",
            question_type="single_choice",
            required=True,
            options=[
                AnswerOption(option_id="A1", label="Under 18"),
                AnswerOption(option_id="A2", label="18–26"),
                AnswerOption(option_id="A3", label="27–35"),
                AnswerOption(option_id="A4", label="36+"),
            ],
            estimated_seconds=10,
        )
    )

    for index, dimension in enumerate(dimensions, start=2):
        name = dimension.name
        normalized = name.lower()
        question_id = f"Q{index:03d}"

        if any(word in normalized for word in ["price", "pay", "willingness"]):
            question = SurveyQuestion(
                question_id=question_id,
                text=f"What is the maximum price you would pay for {topic}?",
                question_type="price_input",
                dimension_mappings={name: 1.0},
                required=True,
                estimated_seconds=20,
            )

        elif any(word in normalized for word in ["occasion", "usage", "frequency"]):
            question = SurveyQuestion(
                question_id=question_id,
                text=f"When would you use {topic}?",
                question_type="multiple_choice",
                dimension_mappings={name: 1.0},
                options=[
                    AnswerOption(option_id="A1", label="At home"),
                    AnswerOption(option_id="A2", label="At work or college"),
                    AnswerOption(option_id="A3", label="While travelling"),
                    AnswerOption(option_id="A4", label="Other"),
                ],
                estimated_seconds=15,
            )

        elif any(word in normalized for word in ["interest", "intent", "demand"]):
            question = SurveyQuestion(
                question_id=question_id,
                text=f"How interested are you in trying {topic}?",
                question_type="likert",
                dimension_mappings={name: 1.0},
                options=[
                    AnswerOption(option_id=f"A{i}", label=label)
                    for i, label in enumerate(
                        [
                            "Not at all interested",
                            "Slightly interested",
                            "Moderately interested",
                            "Very interested",
                            "Extremely interested",
                        ],
                        start=1,
                    )
                ],
                required=True,
                estimated_seconds=10,
            )

        elif any(word in normalized for word in ["safety", "trust", "risk"]):
            question = SurveyQuestion(
                question_id=question_id,
                text=f"How concerned are you about the safety of {topic}?",
                question_type="likert",
                dimension_mappings={name: 1.0},
                options=[
                    AnswerOption(option_id=f"A{i}", label=label)
                    for i, label in enumerate(
                        [
                            "Not concerned",
                            "Slightly concerned",
                            "Moderately concerned",
                            "Very concerned",
                            "Extremely concerned",
                        ],
                        start=1,
                    )
                ],
                estimated_seconds=10,
            )

        else:
            question = SurveyQuestion(
                question_id=question_id,
                text=f"How important is {name} when considering {topic}?",
                question_type="likert",
                dimension_mappings={name: 1.0},
                options=[
                    AnswerOption(option_id=f"A{i}", label=label)
                    for i, label in enumerate(
                        [
                            "Not important",
                            "Slightly important",
                            "Moderately important",
                            "Very important",
                            "Extremely important",
                        ],
                        start=1,
                    )
                ],
                estimated_seconds=10,
            )

        questions.append(question)

    return SurveyBlueprint(
        research_id=research_id,
        title=f"{topic} — Research Survey",
        questions=questions,
    )
