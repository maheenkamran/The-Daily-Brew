from pydantic import BaseModel, Field
from typing import Literal
class Profile(BaseModel):
    name: str
    persona: str
    interests: list[str]
    avoid_topics: list[str] = Field(default_factory=list)
    
class RawArticle(BaseModel):
    url: str
    title: str
    source: str
    published: str = ""
    snippet: str = ""
class EnrichedItem(BaseModel):
    idx: int
    summary: str
    section: Literal["Front Page", "Tech & Code", "Deep Dives", "Quick Briefs"]
    topics: list[str]
    quality_score: float