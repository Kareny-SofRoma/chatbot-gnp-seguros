#!/usr/bin/env python3
"""
Script to process PDF files and upload them to Pinecone
Usage: python scripts/process_pdfs.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fitz  # PyMuPDF
from pathlib import Path
from app.services.embedding_service import embedding_service
from app.services.pinecone_service import pinecone_service
from app.core.database import SessionLocal
from app.models.database import Document
from app.core.logger import get_logger
from datetime import datetime
import uuid

logger = get_logger()

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
PDF_DIRECTORY = Path("data/pdfs")

def extract_text_from_pdf(pdf_path: Path) -> list:
    """Extract text from PDF file page by page"""
    logger.info(f"Processing: {pdf_path.name}")
    
    doc = fitz.open(pdf_path)
    pages_text = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        
        if text.strip():
            pages_text.append({
                'page': page_num + 1,
                'text': text
            })
    
    doc.close()
    logger.info(f"Extracted {len(pages_text)} pages from {pdf_path.name}")
    return pages_text

def chunk_text(text: str, chunk_size: int, overlap: int) -> list:
    """Split text into overlapping chunks"""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        if chunk.strip():
            chunks.append(chunk)
        
        start = end - overlap
    
    return chunks

def process_pdf(pdf_path: Path, db_session):
    """Process a single PDF file"""
    try:
        # Check if already processed
        existing_doc = db_session.query(Document).filter(
            Document.filename == pdf_path.name
        ).first()
        
        if existing_doc and existing_doc.processed:
            logger.info(f"Skipping {pdf_path.name} - already processed")
            return
        
        # Extract text from PDF
        pages_data = extract_text_from_pdf(pdf_path)
        
        if not pages_data:
            logger.warning(f"No text found in {pdf_path.name}")
            return
        
        # Create or update document record
        if not existing_doc:
            doc_record = Document(
                filename=pdf_path.name,
                file_path=str(pdf_path),
                file_size=pdf_path.stat().st_size
            )
            db_session.add(doc_record)
            db_session.commit()
            db_session.refresh(doc_record)
        else:
            doc_record = existing_doc
        
        # Process each page
        all_vectors = []
        total_chunks = 0
        
        for page_data in pages_data:
            page_num = page_data['page']
            page_text = page_data['text']
            
            # Chunk the page text
            chunks = chunk_text(page_text, CHUNK_SIZE, CHUNK_OVERLAP)
            
            for chunk_idx, chunk in enumerate(chunks):
                # Generate embedding
                embedding = embedding_service.generate_embedding(chunk)
                
                # Prepare vector for Pinecone
                vector_id = f"{doc_record.id}_{page_num}_{chunk_idx}"
                metadata = {
                    'filename': pdf_path.name,
                    'page': page_num,
                    'chunk': chunk_idx,
                    'text': chunk,
                    'document_id': str(doc_record.id)
                }
                
                all_vectors.append((vector_id, embedding, metadata))
                total_chunks += 1
        
        # Upload to Pinecone in batches
        batch_size = 100
        for i in range(0, len(all_vectors), batch_size):
            batch = all_vectors[i:i+batch_size]
            pinecone_service.upsert_vectors(batch)
            logger.info(f"Uploaded batch {i//batch_size + 1} for {pdf_path.name}")
        
        # Update document record
        doc_record.processed = True
        doc_record.processed_at = datetime.utcnow()
        doc_record.chunk_count = total_chunks
        db_session.commit()
        
        logger.info(f"✅ Successfully processed {pdf_path.name} - {total_chunks} chunks")
        
    except Exception as e:
        logger.error(f"Error processing {pdf_path.name}: {str(e)}")
        db_session.rollback()
        raise

def main():
    """Main function to process all PDFs"""
    logger.info("Starting PDF processing...")
    
    # Initialize Pinecone index
    logger.info("Initializing Pinecone index...")
    pinecone_service.initialize_index(dimension=1536)
    
    # Get all PDF files
    pdf_files = list(PDF_DIRECTORY.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {PDF_DIRECTORY}")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files")
    
    # Process each PDF
    db = SessionLocal()
    try:
        for pdf_path in pdf_files:
            process_pdf(pdf_path, db)
    finally:
        db.close()
    
    logger.info("✅ PDF processing completed!")

if __name__ == "__main__":
    main()
