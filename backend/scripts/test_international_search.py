#!/usr/bin/env python3
"""
Script para buscar información específica sobre planes internacionales
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.embedding_service import embedding_service
from app.services.pinecone_service import pinecone_service
from app.core.logger import get_logger

logger = get_logger()

def test_international_plans():
    """Buscar información sobre planes internacionales"""
    
    queries = [
        "¿Cuáles son los planes internacionales de GMM?",
        "planes internacionales gastos médicos mayores",
        "cobertura internacional GNP",
        "seguro internacional",
        "planes GMM internacional"
    ]
    
    for query in queries:
        logger.info(f"\n{'='*80}")
        logger.info(f"🔍 Buscando: {query}")
        logger.info(f"{'='*80}\n")
        
        try:
            # Generar embedding
            query_embedding = embedding_service.generate_embedding(query)
            
            # Buscar en Pinecone con más resultados
            results = pinecone_service.query_vectors(
                query_vector=query_embedding,
                top_k=20  # Más resultados para encontrar info
            )
            
            if not results.matches:
                logger.warning("⚠️  NO SE ENCONTRARON RESULTADOS\n")
                continue
            
            logger.info(f"✅ Se encontraron {len(results.matches)} resultados\n")
            
            # Mostrar top 5
            for i, match in enumerate(results.matches[:5], 1):
                logger.info(f"--- Resultado #{i} ---")
                logger.info(f"Score: {match.score:.4f}")
                
                if match.metadata and match.metadata.get('text'):
                    text = match.metadata['text']
                    logger.info(f"Texto: {text[:300]}...")
                    
                    # Buscar keywords relevantes
                    keywords = ['internacional', 'extranjero', 'plan', 'Plus', 'Flex']
                    found_keywords = [k for k in keywords if k.lower() in text.lower()]
                    if found_keywords:
                        logger.info(f"🎯 Keywords encontradas: {found_keywords}")
                
                logger.info("")
            
            # Análisis de scores
            logger.info(f"\n📊 Análisis de scores:")
            scores = [m.score for m in results.matches]
            logger.info(f"Mejor score: {max(scores):.4f}")
            logger.info(f"Score promedio: {sum(scores)/len(scores):.4f}")
            logger.info(f"Scores > 0.7: {len([s for s in scores if s > 0.7])}")
            logger.info(f"Scores > 0.6: {len([s for s in scores if s > 0.6])}")
            logger.info(f"Scores > 0.5: {len([s for s in scores if s > 0.5])}")
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_international_plans()
