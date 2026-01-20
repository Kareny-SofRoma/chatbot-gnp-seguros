#!/usr/bin/env python3
"""
Script de prueba completo del sistema RAG
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.rag_service import rag_service
from app.core.logger import get_logger

logger = get_logger()

def test_rag_complete():
    """Probar el flujo completo de RAG"""
    
    logger.info(f"\n{'='*80}")
    logger.info(f"🤖 PRUEBA COMPLETA DEL SISTEMA RAG")
    logger.info(f"{'='*80}\n")
    
    # Pregunta de prueba
    query = "¿Qué cubre el seguro de gastos médicos mayores de GNP?"
    
    logger.info(f"📝 Pregunta: {query}\n")
    
    try:
        # Ejecutar RAG completo
        logger.info("⚙️  Ejecutando sistema RAG completo...")
        response, sources, tokens = rag_service.query(
            user_query=query,
            conversation_history=None
        )
        
        logger.info(f"\n{'='*80}")
        logger.info(f"✅ RESPUESTA GENERADA")
        logger.info(f"{'='*80}\n")
        
        logger.info(f"🤖 SOIA responde:\n")
        logger.info(response)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 FUENTES CONSULTADAS")
        logger.info(f"{'='*80}\n")
        
        logger.info(f"Total de fuentes: {len(sources)}")
        
        for i, source in enumerate(sources, 1):
            logger.info(f"\n--- Fuente #{i} ---")
            logger.info(f"Source: {source.get('source', 'N/A')}")
            logger.info(f"Line: {source.get('line', 'N/A')}")
            logger.info(f"Lines range: {source.get('lines_from', 'N/A')}-{source.get('lines_to', 'N/A')}")
            logger.info(f"Similarity score: {source.get('score', 0):.3f}")
            logger.info(f"Preview: {source.get('text_preview', 'N/A')[:150]}...")
        
        logger.info(f"\n{'='*80}")
        logger.info(f"📈 ESTADÍSTICAS")
        logger.info(f"{'='*80}\n")
        logger.info(f"Tokens usados: {tokens}")
        logger.info(f"Costo aproximado: ${tokens * 0.000015:.4f} USD")
        
        logger.info(f"\n{'='*80}")
        logger.info(f"✅ PRUEBA COMPLETADA EXITOSAMENTE")
        logger.info(f"{'='*80}\n")
        
    except Exception as e:
        logger.error(f"\n❌ ERROR EN LA PRUEBA:")
        logger.error(str(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rag_complete()
