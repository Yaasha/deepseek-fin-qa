from pydantic import BaseModel


class Score(BaseModel):
    """Score for a QA pair."""

    execution: bool
    program: bool


class Accuracy(BaseModel):
    """Accuracy for a QA dataset."""

    execution: float
    program: float
