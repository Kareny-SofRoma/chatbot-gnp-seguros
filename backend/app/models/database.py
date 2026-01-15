from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.core.database import Base

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    title = Column(String(500), nullable=True)
    
class Message(Base):
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), nullable=False)
    role = Column(String(50), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    tokens_used = Column(Integer, nullable=True)
    model = Column(String(100), nullable=True)
    
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime, nullable=True)
    chunk_count = Column(Integer, default=0)
    metadata = Column(Text, nullable=True)  # JSON string
