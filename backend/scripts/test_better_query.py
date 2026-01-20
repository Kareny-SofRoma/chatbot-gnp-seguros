#!/usr/bin/env python3
"""
Prueba mejorada con reformulación de pregunta
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.rag_service import rag_service
from app.core.logger import get_logger

logger = get_logger()

def test_with_better_query():
    """Probar con pregunta reformulada"""
    
    # Probamos diferentes formulaciones
    queries = [
        "¿Cuáles son los planes internacionales de GMM?",
        "planes internacionales gastos médicos mayores GNP",
        "beneficios planes internacionales GMM"
    ]
    
    for query in queries:
        logger.info(f"\n{'='*80}")
        logger.info(f"🔍 PRUEBA CON: {query}")
        logger.info(f"{'='*80}\n")
        
        try:
            response, sources, tokens = rag_service.query(
                user_query=query,
                conversation_history=None,
                top_k=20  # Más resultados
            )
            
            logger.info(f"\n🤖 SOIA responde:\n")
            logger.info(response[:500] + "..." if len(response) > 500 else response)
            
            logger.info(f"\n📊 Fuentes: {len(sources)}")
            if sources:
                logger.info(f"Mejor score: {sources[0]['score']}")
            
            # Check si es útil
            no_info = "no encontré" in response.lower() or "reformular" in response.lower()
            if not no_info:
                logger.info(f"\n✅ ESTA FORMULACIÓN FUNCIONA!")
                break
            else:
                logger.warning(f"\n⚠️  Esta formulación no funcionó\n")
            
        except Exception as e:
            logger.error(f"Error: {e}")

if __name__ == "__main__":
    test_with_better_query()
