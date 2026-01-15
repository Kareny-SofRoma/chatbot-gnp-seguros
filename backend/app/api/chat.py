from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schemas import ChatRequest, ChatResponse
from app.models.database import Conversation, Message
from app.services.rag_service import rag_service
from app.core.logger import get_logger
from datetime import datetime
import uuid

logger = get_logger()
router = APIRouter(prefix="/api/v1", tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Main chat endpoint
    """
    try:
        # Get or create conversation
        if request.conversation_id:
            conversation_id = uuid.UUID(request.conversation_id)
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
        else:
            # Create new conversation
            conversation = Conversation(
                user_id=request.user_id,
                title=request.message[:100]  # Use first part of message as title
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
        # Save user message
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.message
        )
        db.add(user_message)
        
        # Get conversation history
        history = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at.asc()).all()
        
        conversation_history = []
        for msg in history:
            conversation_history.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Query RAG system
        response_text, sources, tokens_used = rag_service.query(
            user_query=request.message,
            conversation_history=conversation_history[:-1]  # Exclude current message
        )
        
        # Save assistant message
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=response_text,
            tokens_used=tokens_used,
            model="claude-3-5-sonnet"
        )
        db.add(assistant_message)
        
        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Chat response generated for conversation {conversation.id}")
        
        return ChatResponse(
            conversation_id=str(conversation.id),
            message=response_text,
            sources=sources,
            model="claude-3-5-sonnet",
            tokens_used=tokens_used
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """
    Get conversation with all messages
    """
    try:
        conv_uuid = uuid.UUID(conversation_id)
        conversation = db.query(Conversation).filter(
            Conversation.id == conv_uuid
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        messages = db.query(Message).filter(
            Message.conversation_id == conv_uuid
        ).order_by(Message.created_at.asc()).all()
        
        return {
            "conversation": {
                "id": str(conversation.id),
                "user_id": conversation.user_id,
                "title": conversation.title,
                "created_at": conversation.created_at.isoformat(),
                "updated_at": conversation.updated_at.isoformat()
            },
            "messages": [
                {
                    "id": str(msg.id),
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(),
                    "tokens_used": msg.tokens_used
                }
                for msg in messages
            ]
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    except Exception as e:
        logger.error(f"Error getting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations")
async def list_conversations(
    user_id: str = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    List conversations
    """
    try:
        query = db.query(Conversation)
        
        if user_id:
            query = query.filter(Conversation.user_id == user_id)
        
        conversations = query.order_by(
            Conversation.updated_at.desc()
        ).limit(limit).all()
        
        return {
            "conversations": [
                {
                    "id": str(conv.id),
                    "user_id": conv.user_id,
                    "title": conv.title,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat()
                }
                for conv in conversations
            ]
        }
        
    except Exception as e:
        logger.error(f"Error listing conversations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
