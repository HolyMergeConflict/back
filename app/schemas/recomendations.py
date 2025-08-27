from pydantic import BaseModel, Field

class RecommendationItem(BaseModel):
    id: int
    subject: str
    problem: str
    difficulty: float = Field(ge=0)
    relevance_score: float = Field(ge=0)
    match_reason: str

class RecommendationsResponse(BaseModel):
    items: list[RecommendationItem]
