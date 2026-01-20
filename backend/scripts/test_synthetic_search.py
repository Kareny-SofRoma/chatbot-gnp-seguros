#!/usr/bin/env python3
"""
Test: Verificar si los documentos sintéticos están funcionando
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.embedding_service import embedding_service
from app.services.pinecone_service import pinecone_service
from app.core.logger import get_logger

logger = get_logger()

def test_synthetic_docs():
    """Verificar que los docs sintéticos se encuentran bien"""
    
    test_queries = [
        "Lista todos los seguros de GNP",
        "¿Qué productos tiene GNP?",
        "Dame todos los seguros de todas las áreas",
        "Productos de Vida Individual",
        "Seguros de Autos PyMES"
    ]
    
    logger.info("\n" + "="*80)
    logger.info("🔍 VERIFICANDO DOCUMENTOS SINTÉTICOS")
    logger.info("="*80 + "\n")
    
    for query in test_queries:
        logger.info(f"\n{'─'*80}")
        logger.info(f"📝 Query: {query}")
        logger.info(f"{'─'*80}\n")
        
        # Generar embedding
        embedding = embedding_service.generate_embedding(query)
        
        # Buscar
        results = pinecone_service.query_vectors(
            query_vector=embedding,
            top_k=5
        )
        
        logger.info(f"Top 5 resultados:\n")
        
        for i, match in enumerate(results.matches, 1):
            source = match.metadata.get('source', 'N/A')
            doc_type = match.metadata.get('doc_type', 'N/A')
            score = match.score
            text_preview = match.metadata.get('text', '')[:150]
            
            # Marcar si es sintético
            is_synthetic = 'synthetic' in match.id or 'synthetic' in doc_type
            marker = "🟢 SINTÉTICO" if is_synthetic else "🔵 PDF"
            
            logger.info(f"{i}. {marker} - Score: {score:.3f}")
            logger.info(f"   ID: {match.id}")
            logger.info(f"   Tipo: {doc_type}")
            logger.info(f"   Fuente: {source}")
            logger.info(f"   Preview: {text_preview}...")
            logger.info("")
        
        # Análisis
        synthetic_found = any('synthetic' in m.id for m in results.matches[:3])
        best_score = results.matches[0].score if results.matches else 0
        
        if synthetic_found and best_score > 0.7:
            logger.info("✅ BUENO: Encontró documento sintético con buen score")
        elif synthetic_found:
            logger.warning(f"⚠️  Encontró sintético pero score bajo ({best_score:.3f})")
        else:
            logger.error("❌ PROBLEMA: No encontró documentos sintéticos en top 3")

if __name__ == "__main__":
    test_synthetic_docs()
