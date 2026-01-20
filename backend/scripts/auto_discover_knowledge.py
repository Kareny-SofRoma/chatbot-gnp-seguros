#!/usr/bin/env python3
"""
Script de "Knowledge Discovery" automático
Analiza Pinecone y crea documentos sintéticos automáticamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.embedding_service import embedding_service
from app.services.pinecone_service import pinecone_service
from app.core.logger import get_logger
import random
import re

logger = get_logger()

def discover_products():
    """Descubrir productos automáticamente buscando en Pinecone"""
    
    logger.info(f"\n{'='*80}")
    logger.info("🔍 DESCUBRIENDO PRODUCTOS EN PINECONE")
    logger.info(f"{'='*80}\n")
    
    # Buscar menciones de productos con diferentes queries
    search_queries = [
        "productos GMM GNP seguros",
        "planes gastos médicos mayores",
        "seguro médico GNP",
        "cobertura GMM",
        "plan Premium Platino",
        "internacional Enlace Vínculo"
    ]
    
    all_products = set()
    all_contexts = []
    
    for query in search_queries:
        logger.info(f"🔍 Buscando: {query}")
        
        try:
            embedding = embedding_service.generate_embedding(query)
            results = pinecone_service.query_vectors(
                query_vector=embedding,
                top_k=30
            )
            
            for match in results.matches:
                if match.score > 0.6:
                    text = match.metadata.get('text', '')
                    all_contexts.append(text)
                    
                    # Extraer nombres de productos (palabras capitalizadas específicas)
                    products = re.findall(r'\b(Premium|Platino|Flex|Versátil|Conexión|Indemniza|Acceso|Esencial|Plenitud|VIP|Internacional|Enlace|Vínculo|Mundial|Alta Especialidad)\b', text)
                    all_products.update(products)
            
            logger.info(f"   Encontrados: {len(results.matches)} resultados")
            
        except Exception as e:
            logger.warning(f"   Error: {e}")
    
    logger.info(f"\n📊 DESCUBRIMIENTO COMPLETO:")
    logger.info(f"   Total productos únicos encontrados: {len(all_products)}")
    logger.info(f"   Total contextos analizados: {len(all_contexts)}")
    
    return all_products, all_contexts

def create_synthetic_index(products, contexts):
    """Crear documento sintético basado en lo descubierto"""
    
    logger.info(f"\n{'='*80}")
    logger.info("📝 CREANDO DOCUMENTO SINTÉTICO")
    logger.info(f"{'='*80}\n")
    
    # Organizar productos por categoría (basado en patrones encontrados)
    categorized = {
        'Premium/Platino': [p for p in products if p in ['Premium', 'Platino']],
        'Flexibles': [p for p in products if p in ['Flex', 'Versátil', 'Conexión']],
        'Básicos': [p for p in products if p in ['Acceso', 'Esencial', 'Plenitud', 'VIP', 'Indemniza']],
        'Internacionales': [p for p in products if p in ['Internacional', 'Enlace', 'Vínculo', 'Mundial', 'Alta Especialidad']]
    }
    
    # Generar texto del documento sintético
    synthetic_text = "PRODUCTOS Y PLANES DE GASTOS MÉDICOS MAYORES (GMM) DE GNP\n\n"
    synthetic_text += "GNP ofrece una amplia gama de productos de seguros de Gastos Médicos Mayores:\n\n"
    
    for category, prods in categorized.items():
        if prods:
            synthetic_text += f"**{category}:**\n"
            for prod in sorted(prods):
                synthetic_text += f"• {prod}\n"
            synthetic_text += "\n"
    
    # Agregar contexto adicional de los fragmentos encontrados
    synthetic_text += "\nINFORMACIÓN ADICIONAL:\n"
    synthetic_text += "Cada producto tiene diferentes niveles de cobertura, deducibles y beneficios. "
    synthetic_text += "Los planes internacionales ofrecen cobertura fuera de México. "
    synthetic_text += "Los planes flexibles permiten personalización según necesidades del cliente.\n"
    
    logger.info(f"✅ Documento sintético creado ({len(synthetic_text)} caracteres)")
    
    return synthetic_text

def upload_synthetic_doc(text):
    """Subir documento sintético a Pinecone"""
    
    logger.info(f"\n{'='*80}")
    logger.info("⬆️  SUBIENDO A PINECONE")
    logger.info(f"{'='*80}\n")
    
    try:
        # Generar embedding
        embedding = embedding_service.generate_embedding(text)
        
        # Preparar metadata
        metadata = {
            'text': text,
            'source': 'Índice Automático de Productos GNP',
            'blobType': 'synthetic/auto-generated',
            'line': 0.0,
            'loc.lines.from': 0.0,
            'loc.lines.to': 0.0,
            'doc_type': 'synthetic_index',
            'category': 'productos_gmm_auto'
        }
        
        # Subir
        vector_id = "synthetic-auto-productos-gmm"
        pinecone_service.upsert_vectors([(vector_id, embedding, metadata)])
        
        logger.info("✅ Documento sintético subido exitosamente")
        logger.info(f"   ID: {vector_id}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error subiendo documento: {e}")
        return False

def main():
    """Proceso principal de auto-discovery"""
    
    logger.info("\n" + "="*80)
    logger.info("🤖 KNOWLEDGE DISCOVERY AUTOMÁTICO")
    logger.info("="*80)
    logger.info("\nEste script descubrirá automáticamente qué productos existen")
    logger.info("en tus PDFs y creará un índice sintético sin que tengas que")
    logger.info("pasar ninguna información manualmente.\n")
    
    # Fase 1: Descubrir
    logger.info("FASE 1: Descubrimiento\n")
    products, contexts = discover_products()
    
    if not products:
        logger.warning("\n⚠️  No se encontraron productos. Verifica la conexión a Pinecone.")
        return
    
    logger.info(f"\n✅ Productos descubiertos:")
    for p in sorted(products):
        logger.info(f"   • {p}")
    
    # Fase 2: Crear documento
    logger.info("\nFASE 2: Creación de índice\n")
    synthetic_text = create_synthetic_index(products, contexts)
    
    logger.info("\n📄 Vista previa del documento:")
    logger.info("-" * 80)
    logger.info(synthetic_text[:500] + "...")
    logger.info("-" * 80)
    
    # Fase 3: Subir
    logger.info("\nFASE 3: Upload a Pinecone\n")
    success = upload_synthetic_doc(synthetic_text)
    
    if success:
        logger.info(f"\n{'='*80}")
        logger.info("✅ PROCESO COMPLETADO EXITOSAMENTE")
        logger.info(f"{'='*80}\n")
        logger.info("💡 Ahora el chatbot podrá responder preguntas como:")
        logger.info("   • ¿Qué productos de GMM tiene GNP?")
        logger.info("   • Lista todos los planes de seguros")
        logger.info("   • ¿Cuáles son los planes internacionales?")
    else:
        logger.error("\n❌ El proceso falló. Revisa los logs arriba.")

if __name__ == "__main__":
    main()
