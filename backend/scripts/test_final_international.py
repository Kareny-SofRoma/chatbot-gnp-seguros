#!/usr/bin/env python3
"""
Test definitivo de planes internacionales
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.rag_service import rag_service
from app.core.logger import get_logger

logger = get_logger()

def test_international_plans_final():
    """Test final con query expansion"""
    
    query = "¿Cuáles son los planes internacionales de GMM?"
    
    logger.info(f"\n{'='*80}")
    logger.info(f"🔍 PRUEBA FINAL: Planes Internacionales GMM")
    logger.info(f"{'='*80}\n")
    
    logger.info(f"📝 Pregunta del usuario: {query}\n")
    
    try:
        logger.info("⚙️  Ejecutando RAG con query expansion...\n")
        
        response, sources, tokens = rag_service.query(
            user_query=query,
            conversation_history=None
        )
        
        logger.info(f"{'='*80}")
        logger.info(f"✅ RESPUESTA DE SOIA")
        logger.info(f"{'='*80}\n")
        
        logger.info(response)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 ANÁLISIS DE FUENTES")
        logger.info(f"{'='*80}\n")
        
        logger.info(f"Total fuentes encontradas: {len(sources)}")
        logger.info(f"Mejor score: {sources[0]['score'] if sources else 'N/A'}")
        logger.info(f"Tokens usados: {tokens}")
        logger.info(f"Costo: ${tokens * 0.000015:.4f} USD\n")
        
        if sources:
            logger.info("🎯 Top 5 fragmentos encontrados:\n")
            for i, source in enumerate(sources[:5], 1):
                logger.info(f"{i}. Score: {source['score']:.3f}")
                logger.info(f"   Texto: {source['text_preview'][:200]}")
                logger.info("")
        
        # Evaluar calidad de respuesta
        response_lower = response.lower()
        
        keywords_good = ['plan', 'internacional', 'plus', 'flex', 'cobertura']
        keywords_bad = ['no encontré', 'no tengo información', 'reformular']
        
        found_good = sum(1 for k in keywords_good if k in response_lower)
        found_bad = sum(1 for k in keywords_bad if k in response_lower)
        
        logger.info(f"{'='*80}")
        logger.info(f"📈 EVALUACIÓN DE CALIDAD")
        logger.info(f"{'='*80}\n")
        
        if found_bad > 0:
            logger.warning("⚠️  RESPUESTA NO SATISFACTORIA")
            logger.warning(f"   Encontró keywords negativas: {found_bad}")
            logger.info("\n💡 El problema puede ser:")
            logger.info("   1. El contexto no tiene suficiente detalle de los planes")
            logger.info("   2. Los PDFs necesitan mejor procesamiento")
            logger.info("   3. Necesitamos expandir más las búsquedas")
        else:
            logger.info("✅ RESPUESTA SATISFACTORIA")
            logger.info(f"   Menciona {found_good} conceptos clave")
            logger.info("   La respuesta parece útil para el agente")
        
    except Exception as e:
        logger.error(f"\n❌ ERROR:")
        logger.error(str(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_international_plans_final()
