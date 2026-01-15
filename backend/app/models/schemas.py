from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    sources: List[dict] = []
    model: str
    tokens_used: Optional[int] = None

class MessageSchema(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationSchema(BaseModel):
    id: UUID
    user_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    title: Optional[str]
    
    class Config:
        from_attributes = True

class ConversationWithMessages(ConversationSchema):
    messages: List[MessageSchema] = []

class DocumentSchema(BaseModel):
    id: UUID
    filename: str
    file_size: Optional[int]
    uploaded_at: datetime
    processed: bool
    chunk_count: int
    
    class Config:
        from_attributes = True
