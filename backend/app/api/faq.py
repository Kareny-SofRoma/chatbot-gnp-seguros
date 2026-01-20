from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.database import FAQ
from app.models.schemas import FAQCreate, FAQResponse, FAQBatchProcessResponse
from app.services.rag_service import rag_service
from app.core.logger import get_logger
from typing import List
import json

router = APIRouter(prefix="/api/v1/faq", tags=["faq"])
logger = get_logger()

@router.post("/batch-process", response_model=FAQBatchProcessResponse)
async def batch_process_faqs(
    faq_data: FAQCreate,
    db: Session = Depends(get_db)
):
    """
    Process a batch of FAQ questions and cache their answers.
    This endpoint should be called once to pre-generate answers for all FAQs.
    """
    try:
        processed = 0
        failed = 0
        faqs_created = []
        
        for question in faq_data.questions:
            try:
                # Check if FAQ already exists
                existing_faq = db.query(FAQ).filter(FAQ.question == question).first()
                
                if existing_faq:
                    logger.info(f"FAQ already exists: {question}")
                    faqs_created.append(existing_faq)
                    processed += 1
                    continue
                
                # Generate answer using RAG
                logger.info(f"Processing FAQ: {question}")
                answer, sources, tokens_used = rag_service.query(
                    user_query=question,
                    conversation_history=None,
                    top_k=5
                )
                
                # Create FAQ record
                faq = FAQ(
                    question=question,
                    answer=answer,
                    category=faq_data.category,
                    sources=json.dumps(sources, ensure_ascii=False),
                    tokens_used=tokens_used,
                    is_active=True,
                    views_count=0
                )
                
                db.add(faq)
                db.commit()
                db.refresh(faq)
                
                faqs_created.append(faq)
                processed += 1
                
                logger.info(f"Successfully processed FAQ: {question}")
                
            except Exception as e:
                logger.error(f"Error processing FAQ '{question}': {str(e)}")
                failed += 1
                continue
        
        # Convert to response format
        faq_responses = []
        for faq in faqs_created:
            sources_list = json.loads(faq.sources) if faq.sources else []
            faq_responses.append(FAQResponse(
                id=faq.id,
                question=faq.question,
                answer=faq.answer,
                category=faq.category,
                sources=sources_list,
                views_count=faq.views_count,
                created_at=faq.created_at,
                updated_at=faq.updated_at
            ))
        
        return FAQBatchProcessResponse(
            processed=processed,
            failed=failed,
            total=len(faq_data.questions),
            faqs=faq_responses
        )
        
    except Exception as e:
        logger.error(f"Error in batch FAQ processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=List[FAQResponse])
async def list_faqs(
    category: str = None,
    db: Session = Depends(get_db)
):
    """
    Get all active FAQs, optionally filtered by category.
    Returns cached answers without querying the LLM.
    """
    try:
        query = db.query(FAQ).filter(FAQ.is_active == True)
        
        if category:
            query = query.filter(FAQ.category == category)
        
        faqs = query.order_by(FAQ.created_at.desc()).all()
        
        # Convert to response format
        faq_responses = []
        for faq in faqs:
            sources_list = json.loads(faq.sources) if faq.sources else []
            faq_responses.append(FAQResponse(
                id=faq.id,
                question=faq.question,
                answer=faq.answer,
                category=faq.category,
                sources=sources_list,
                views_count=faq.views_count,
                created_at=faq.created_at,
                updated_at=faq.updated_at
            ))
        
        return faq_responses
        
    except Exception as e:
        logger.error(f"Error listing FAQs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{faq_id}", response_model=FAQResponse)
async def get_faq(
    faq_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific FAQ by ID and increment its view count.
    """
    try:
        faq = db.query(FAQ).filter(FAQ.id == faq_id, FAQ.is_active == True).first()
        
        if not faq:
            raise HTTPException(status_code=404, detail="FAQ not found")
        
        # Increment view count
        faq.views_count += 1
        db.commit()
        db.refresh(faq)
        
        sources_list = json.loads(faq.sources) if faq.sources else []
        
        return FAQResponse(
            id=faq.id,
            question=faq.question,
            answer=faq.answer,
            category=faq.category,
            sources=sources_list,
            views_count=faq.views_count,
            created_at=faq.created_at,
            updated_at=faq.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting FAQ: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{faq_id}")
async def delete_faq(
    faq_id: str,
    db: Session = Depends(get_db)
):
    """
    Soft delete an FAQ (mark as inactive).
    """
    try:
        faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
        
        if not faq:
            raise HTTPException(status_code=404, detail="FAQ not found")
        
        faq.is_active = False
        db.commit()
        
        return {"message": "FAQ deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting FAQ: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
