from pydantic import BaseModel, Field

class Profile(BaseModel):
    name: str
    persona: str
    interests: list[str]
    avoid_topics: list[str] = Field(default_factory=list)