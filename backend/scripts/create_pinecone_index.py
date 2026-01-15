#!/usr/bin/env python3
"""
Script to create Pinecone index
Usage: python scripts/create_pinecone_index.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.pinecone_service import pinecone_service
from app.core.logger import get_logger

logger = get_logger()

def main():
    """Create Pinecone index"""
    logger.info("Creating Pinecone index...")
    
    try:
        pinecone_service.initialize_index(dimension=1536)
        logger.info("✅ Pinecone index created successfully!")
    except Exception as e:
        logger.error(f"❌ Error creating index: {str(e)}")
        raise

if __name__ == "__main__":
    main()
