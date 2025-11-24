from pydantic import BaseModel, Field
from datetime import datetime


class Comment(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str = Field(...)
    content: str = Field(...)
    timestamp: str = Field(...)
    score: float = Field(..., ge=0, le=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None
    updated_at: datetime | None = None


class Message(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str = Field(...)
    text: str = Field(...)
    timestamp: str = Field(...)
    type: str = Field(...)