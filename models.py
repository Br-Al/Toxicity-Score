from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class Comment(BaseModel):
    id: str = Field(...)
    user_id: str = Field(...)
    content: str = Field(...)
    timestamp: str = Field(...)
    score: float = Field(..., ge=0, le=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None
    updated_at: datetime | None = None


class Message(BaseModel):
    id: str = Field(alias="_id", default_factory=lambda: str(uuid.uuid4()))
    type: str = Field(...)
    status: str = Field(...)
    message_id: str = Field(...)
    processed_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
