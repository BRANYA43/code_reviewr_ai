from enum import StrEnum

from openai import BaseModel
from pydantic import HttpUrl


class CandidateLevel(StrEnum):
    JUNIOR = 'junior'
    MIDDLE = 'middle'
    SENIOR = 'senior'


class ReviewInputSchema(BaseModel):
    assignment_description: str
    github_repo_url: HttpUrl
    candidate_level: CandidateLevel
