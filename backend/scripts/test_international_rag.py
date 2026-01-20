#!/usr/bin/env python3
"""
Prueba RAG con pregunta específica de planes internacionales
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.rag_service import rag_service
from app.core.logger import get_logger

logger = get_logger()

def test_specific_question():
    """Probar pregunta específica sobre planes internacionales"""
    
    query = "¿Cuáles son los planes internacionales de GMM?"
    
    logger.info(f"\n{'='*80}")
    logger.info(f"🔍 PRUEBA: Planes Internacionales GMM")
    logger.info(f"{'='*80}\n")
    
    logger.info(f"📝 Pregunta: {query}\n")
    
    try:
        # Ejecutar RAG con diferentes configuraciones
        logger.info("⚙️  Probando con TOP_K = 15 y threshold más bajo...\n")
        
        response, sources, tokens = rag_service.query(
            user_query=query,
            conversation_history=None,
            top_k=15  # Más resultados
        )
        
        logger.info(f"\n{'='*80}")
        logger.info(f"✅ RESPUESTA GENERADA")
        logger.info(f"{'='*80}\n")
        
        logger.info(f"🤖 SOIA dice:\n")
        logger.info(response)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 ANÁLISIS")
        logger.info(f"{'='*80}\n")
        
        logger.info(f"Fuentes encontradas: {len(sources)}")
        logger.info(f"Tokens usados: {tokens}")
        
        if sources:
            logger.info(f"\n🎯 Top 3 fuentes:")
            for i, source in enumerate(sources[:3], 1):
                logger.info(f"\n  {i}. Score: {source['score']:.3f}")
                logger.info(f"     Preview: {source['text_preview'][:150]}...")
        else:
            logger.warning("\n⚠️  NO SE ENCONTRARON FUENTES")
        
        # Verificar si la respuesta es de "no encontré información"
        no_info_keywords = [
            "no encontré",
            "no tengo información",
            "no está disponible",
            "reformular tu pregunta"
        ]
        
        response_lower = response.lower()
        has_no_info = any(keyword in response_lower for keyword in no_info_keywords)
        
        if has_no_info:
            logger.warning("\n⚠️  LA RESPUESTA INDICA QUE NO ENCONTRÓ INFORMACIÓN")
            logger.info("\n💡 SUGERENCIAS:")
            logger.info("   1. Bajar el threshold de 0.6 a 0.5")
            logger.info("   2. Aumentar TOP_K a 20")
            logger.info("   3. Verificar que los PDFs tengan esa información")
            logger.info("   4. Revisar cómo se procesaron los PDFs en n8n")
        else:
            logger.info("\n✅ LA RESPUESTA PARECE TENER INFORMACIÓN ÚTIL")
        
    except Exception as e:
        logger.error(f"\n❌ ERROR:")
        logger.error(str(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_specific_question()
