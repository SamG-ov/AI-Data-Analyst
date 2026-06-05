"""Schemas for natural-language Q&A about a dataset."""

from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    """A user's natural-language question about a dataset."""

    question: str = Field(min_length=1, max_length=2000)


class AnswerResponse(BaseModel):
    """Claude's natural-language answer."""

    answer: str


class InsightsResponse(BaseModel):
    """Claude's analytical write-up (summary, findings, recommendations)."""

    report: str
