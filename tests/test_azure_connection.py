from pydantic import BaseModel

from app.services.gemini_client import generate_structured_output


class ConnectionTest(BaseModel):
    message: str
    status: str


if __name__ == "__main__":
    result = generate_structured_output(
        prompt=(
            "Return a JSON object with message='Azure connected' "
            "and status='success'."
        ),
        output_model=ConnectionTest,
    )

    print(result.model_dump())