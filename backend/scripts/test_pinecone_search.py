#!/usr/bin/env python3
"""
Script de debugging para probar búsqueda en Pinecone
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.embedding_service import embedding_service
from app.services.pinecone_service import pinecone_service
from app.core.logger import get_logger

logger = get_logger()

def test_search():
    """Probar búsqueda en Pinecone"""
    
    # Pregunta de prueba
    query = "¿Qué cubre el seguro de gastos médicos mayores?"
    
    logger.info(f"\n{'='*80}")
    logger.info(f"🔍 PRUEBA DE BÚSQUEDA EN PINECONE")
    logger.info(f"{'='*80}\n")
    
    logger.info(f"📝 Pregunta: {query}\n")
    
    # 1. Generar embedding
    logger.info("⚙️  Paso 1: Generando embedding...")
    try:
        query_embedding = embedding_service.generate_embedding(query)
        logger.info(f"✅ Embedding generado - Dimensión: {len(query_embedding)}")
        logger.info(f"   Primeros 5 valores: {query_embedding[:5]}\n")
    except Exception as e:
        logger.error(f"❌ Error generando embedding: {e}")
        return
    
    # 2. Buscar en Pinecone
    logger.info("⚙️  Paso 2: Buscando en Pinecone...")
    try:
        results = pinecone_service.query_vectors(
            query_vector=query_embedding,
            top_k=10  # Buscar top 10 para debugging
        )
        
        logger.info(f"✅ Búsqueda completada\n")
        
        # 3. Analizar resultados
        logger.info(f"{'='*80}")
        logger.info(f"📊 RESULTADOS:")
        logger.info(f"{'='*80}\n")
        
        if not results.matches:
            logger.warning("⚠️  NO SE ENCONTRARON RESULTADOS")
            return
        
        logger.info(f"✅ Se encontraron {len(results.matches)} resultados\n")
        
        for i, match in enumerate(results.matches, 1):
            logger.info(f"--- Resultado #{i} ---")
            logger.info(f"ID: {match.id}")
            logger.info(f"Score: {match.score:.4f}")
            logger.info(f"Metadata keys: {list(match.metadata.keys()) if match.metadata else 'None'}")
            
            if match.metadata:
                logger.info(f"\n📄 Metadata completa:")
                for key, value in match.metadata.items():
                    if key == 'text' and value:
                        # Mostrar solo primeros 200 chars del texto
                        logger.info(f"  {key}: {value[:200]}...")
                    else:
                        logger.info(f"  {key}: {value}")
            
            logger.info("")
        
        # 4. Ver qué scores están por encima del threshold
        logger.info(f"\n{'='*80}")
        logger.info(f"🎯 ANÁLISIS DE SCORES:")
        logger.info(f"{'='*80}\n")
        
        above_threshold = [m for m in results.matches if m.score > 0.6]
        logger.info(f"Threshold actual: 0.6")
        logger.info(f"Resultados por encima del threshold: {len(above_threshold)}")
        
        if above_threshold:
            logger.info(f"✅ Scores encontrados: {[round(m.score, 3) for m in above_threshold]}")
        else:
            logger.warning(f"⚠️  Ningún resultado supera el threshold de 0.6")
            logger.info(f"   Mejores scores: {[round(m.score, 3) for m in results.matches[:5]]}")
            logger.info(f"\n💡 Sugerencia: Considera bajar el threshold a 0.5 o menos")
        
    except Exception as e:
        logger.error(f"❌ Error en búsqueda: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search()
