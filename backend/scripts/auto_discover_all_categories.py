#!/usr/bin/env python3
"""
Knowledge Discovery Completo - Todas las áreas de GNP
Descubre automáticamente productos y organiza información por categoría
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.embedding_service import embedding_service
from app.services.pinecone_service import pinecone_service
from app.core.logger import get_logger
import re
from collections import defaultdict

logger = get_logger()

# ESTRUCTURA COMPLETA DE GNP
GNP_STRUCTURE = {
    'GMM': {
        'name': 'Gastos Médicos Mayores',
        'segments': ['Individual', 'PyMES y Corporativo'],
        'search_terms': [
            'gastos médicos mayores',
            'GMM seguro salud',
            'cobertura médica',
            'hospitalización',
            'planes GMM',
            'seguro médico GNP'
        ],
        'product_keywords': [
            'Premium', 'Platino', 'Flex', 'Versátil', 'Conexión',
            'Indemniza', 'Acceso', 'Esencial', 'Plenitud', 'VIP',
            'Internacional', 'Enlace', 'Vínculo', 'Mundial', 'Alta Especialidad'
        ]
    },
    'Vida': {
        'name': 'Seguros de Vida',
        'segments': ['Individual', 'PyMES y Corporativo'],
        'search_terms': [
            'seguro de vida',
            'vida individual',
            'vida grupo',
            'protección vida',
            'beneficiarios vida',
            'póliza vida GNP'
        ],
        'product_keywords': [
            'Dotal', 'Temporal', 'Ordinario', 'Universal', 'Vitalicio',
            'Inversión', 'Ahorro', 'Protección'
        ]
    },
    'Autos': {
        'name': 'Seguros de Autos',
        'segments': ['Individual', 'PyMES y Corporativo'],
        'search_terms': [
            'seguro auto',
            'seguro vehicular',
            'cobertura automóvil',
            'póliza auto',
            'seguro coche GNP',
            'RC vehículo'
        ],
        'product_keywords': [
            'Amplia', 'Limitada', 'RC', 'Responsabilidad Civil',
            'Cobertura Total', 'Plus', 'Básico'
        ]
    },
    'Daños': {
        'name': 'Seguros de Daños',
        'segments': ['Individual', 'PyMES y Corporativo'],
        'search_terms': [
            'seguro daños',
            'seguro hogar',
            'seguro empresarial',
            'protección patrimonio',
            'daños materiales',
            'seguro comercio'
        ],
        'product_keywords': [
            'Hogar', 'Comercio', 'Empresarial', 'Incendio', 'Robo',
            'Responsabilidad', 'Todo Riesgo'
        ]
    }
}

def discover_category(category_key, category_info):
    """Descubrir información de una categoría específica"""
    
    logger.info(f"\n{'='*80}")
    logger.info(f"🔍 DESCUBRIENDO: {category_info['name']}")
    logger.info(f"{'='*80}\n")
    
    discovered_products = set()
    relevant_contexts = []
    
    # Buscar con cada término
    for term in category_info['search_terms']:
        logger.info(f"   Buscando: {term}")
        
        try:
            embedding = embedding_service.generate_embedding(term)
            results = pinecone_service.query_vectors(
                query_vector=embedding,
                top_k=20
            )
            
            found_count = 0
            for match in results.matches:
                if match.score > 0.55:  # Threshold más permisivo
                    text = match.metadata.get('text', '')
                    
                    # Buscar keywords de productos
                    for keyword in category_info['product_keywords']:
                        if keyword.lower() in text.lower():
                            discovered_products.add(keyword)
                    
                    # Guardar contextos relevantes
                    if len(text) > 100:  # Solo textos sustanciales
                        relevant_contexts.append({
                            'text': text[:500],
                            'score': match.score
                        })
                        found_count += 1
            
            logger.info(f"      ✓ {found_count} chunks relevantes")
            
        except Exception as e:
            logger.warning(f"      ✗ Error: {e}")
    
    logger.info(f"\n   📊 Productos descubiertos: {len(discovered_products)}")
    for prod in sorted(discovered_products):
        logger.info(f"      • {prod}")
    
    return discovered_products, relevant_contexts

def create_category_synthetic_doc(category_key, category_info, products, contexts):
    """Crear documento sintético para una categoría"""
    
    doc_text = f"PRODUCTOS DE {category_info['name'].upper()} - GNP\n\n"
    
    # Segmentos
    doc_text += f"GNP ofrece seguros de {category_info['name']} para:\n"
    for segment in category_info['segments']:
        doc_text += f"• {segment}\n"
    doc_text += "\n"
    
    # Productos descubiertos
    if products:
        doc_text += "PRODUCTOS DISPONIBLES:\n"
        for product in sorted(products):
            doc_text += f"• {product}\n"
        doc_text += "\n"
    
    # Información adicional de contextos
    doc_text += "INFORMACIÓN GENERAL:\n"
    doc_text += f"Los seguros de {category_info['name']} de GNP ofrecen diferentes niveles de cobertura "
    doc_text += f"según las necesidades del cliente. Disponibles tanto para personas físicas "
    doc_text += f"(Individual) como para empresas (PyMES y Corporativo).\n\n"
    
    # Agregar fragmentos de contexto más relevantes
    if contexts:
        doc_text += "DETALLES ADICIONALES:\n"
        # Tomar los 3 contextos con mejor score
        top_contexts = sorted(contexts, key=lambda x: x['score'], reverse=True)[:3]
        for ctx in top_contexts:
            # Limpiar y agregar fragmento
            clean_text = ctx['text'].replace('\n', ' ').strip()
            if len(clean_text) > 50:
                doc_text += f"{clean_text[:300]}...\n\n"
    
    return doc_text

def upload_category_doc(category_key, doc_text):
    """Subir documento sintético de categoría a Pinecone"""
    
    try:
        # Generar embedding
        embedding = embedding_service.generate_embedding(doc_text)
        
        # Metadata
        metadata = {
            'text': doc_text,
            'source': f'Índice Automático {category_key}',
            'blobType': 'synthetic/category-index',
            'line': 0.0,
            'loc.lines.from': 0.0,
            'loc.lines.to': 0.0,
            'doc_type': 'synthetic_category_index',
            'category': category_key.lower()
        }
        
        # Subir
        vector_id = f"synthetic-auto-{category_key.lower()}"
        pinecone_service.upsert_vectors([(vector_id, embedding, metadata)])
        
        logger.info(f"   ✅ Subido a Pinecone (ID: {vector_id})")
        return True
        
    except Exception as e:
        logger.error(f"   ❌ Error subiendo: {e}")
        return False

def main():
    """Proceso principal - descubrir todas las categorías"""
    
    logger.info("\n" + "="*80)
    logger.info("🤖 KNOWLEDGE DISCOVERY - TODAS LAS ÁREAS DE GNP")
    logger.info("="*80)
    logger.info("\nCategorías a procesar:")
    for key, info in GNP_STRUCTURE.items():
        logger.info(f"   • {key}: {info['name']}")
    logger.info("\n")
    
    results = {}
    
    # Procesar cada categoría
    for category_key, category_info in GNP_STRUCTURE.items():
        
        # Descubrir
        products, contexts = discover_category(category_key, category_info)
        
        # Crear documento
        logger.info(f"\n   📝 Creando documento sintético...")
        doc_text = create_category_synthetic_doc(
            category_key, 
            category_info, 
            products, 
            contexts
        )
        
        logger.info(f"   📄 Tamaño: {len(doc_text)} caracteres")
        
        # Subir a Pinecone
        logger.info(f"   ⬆️  Subiendo a Pinecone...")
        success = upload_category_doc(category_key, doc_text)
        
        results[category_key] = {
            'success': success,
            'products': len(products),
            'doc_size': len(doc_text)
        }
        
        logger.info("")
    
    # Resumen final
    logger.info("\n" + "="*80)
    logger.info("📊 RESUMEN FINAL")
    logger.info("="*80 + "\n")
    
    total_success = sum(1 for r in results.values() if r['success'])
    total_products = sum(r['products'] for r in results.values())
    
    logger.info(f"✅ Categorías procesadas: {total_success}/{len(results)}")
    logger.info(f"✅ Total productos descubiertos: {total_products}\n")
    
    for cat, res in results.items():
        status = "✅" if res['success'] else "❌"
        logger.info(f"{status} {cat}: {res['products']} productos")
    
    if total_success == len(results):
        logger.info("\n" + "="*80)
        logger.info("🎉 PROCESO COMPLETADO EXITOSAMENTE")
        logger.info("="*80 + "\n")
        logger.info("💡 El chatbot ahora puede responder preguntas como:\n")
        logger.info("   • ¿Qué productos de Vida tiene GNP?")
        logger.info("   • ¿Cuáles son los seguros de Autos?")
        logger.info("   • Lista todos los productos de GMM")
        logger.info("   • ¿Qué seguros de Daños ofrecen?")
        logger.info("   • Compara productos Individual vs PyMES\n")
    else:
        logger.warning("\n⚠️  Algunas categorías fallaron. Revisa los logs.")

if __name__ == "__main__":
    main()
