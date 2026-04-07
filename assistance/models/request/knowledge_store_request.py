from pydantic import BaseModel, Field

class KnowledgeStoreRequest(BaseModel):
    content: str = Field(..., min_length=1)
    category: str = "fact"
    tags: list[str] = Field(default_factory=list)
