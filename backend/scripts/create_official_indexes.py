#!/usr/bin/env python3
"""
Knowledge Discovery Completo v2 - Con productos reales de GNP
Crea índices sintéticos usando la estructura real proporcionada
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.embedding_service import embedding_service
from app.services.pinecone_service import pinecone_service
from app.core.logger import get_logger

logger = get_logger()

# ESTRUCTURA REAL COMPLETA DE GNP
GNP_PRODUCTS = {
    'GMM': {
        'Individual': {
            'name': 'Gastos Médicos Mayores Individual',
            'products': [
                'Premium', 'Platino', 'Flexibles', 'Versátil',
                'Conexión GNP', 'Conexión Línea Azul',
                'GNP Indemniza', 'Acceso', 'Esencial', 'Plenitud', 'VIP',
                'Internacional', 'GNP Enlace Internacional', 
                'Vínculo Mundial', 'Alta Especialidad'
            ]
        },
        'PyMES_Corporativo': {
            'name': 'Gastos Médicos Mayores PyMES y Corporativo',
            'products': [
                'GMM Grupo', 'GNP Indemniza', 'Respaldo Hospitalario',
                'Línea Azul VIP', 'Línea Azul Internacional', 
                'Línea Azul Premier', 'Seguro por Hospitalización',
                'Accidentes Personales'
            ]
        }
    },
    'Vida': {
        'Individual': {
            'name': 'Vida Individual',
            'products': {
                'Protección y Ahorro': [
                    'Visión Plus', 'Privilegio Universal', 'Trasciende',
                    'Ordinario de Vida', 'Platino Universal'
                ],
                'Retiro': [
                    'Consolida', 'Proyecta', 'Proyecta Afecto',
                    'Consolida Total', 'Elige'
                ],
                'Ahorro': [
                    'Vida a tus sueños', 'Dotal', 'Inversión',
                    'Capitaliza', 'Vida Inversión'
                ],
                'Educación': [
                    'Profesional Abuelos', 'Profesional'
                ],
                'Protección': [
                    'Platino', 'Privilegio'
                ]
            }
        },
        'PyMES_Corporativo': {
            'name': 'Vida PyMES y Corporativo',
            'products': [
                'Vida Grupo', 'GNP Vida Deudor', 'Vida Escolar GNP'
            ]
        }
    },
    'Autos': {
        'Individual': {
            'name': 'Autos Individual',
            'products': [
                'Auto Más', 'Auto Élite', 'Motos',
                'Automóviles Individual', 'Auto Más Información C.',
                'Autos Turistas GNP'
            ]
        },
        'PyMES_Corporativo': {
            'name': 'Autos PyMES y Corporativo',
            'products': [
                'Flotillas PyMEs y Corporativo', 'Micronegocio'
            ]
        }
    },
    'Daños': {
        'Individual': {
            'name': 'Daños Individual',
            'products': [
                'GNP Riesgos Naturales', 'Mi Mascota GNP',
                'Hogar versátil'
            ]
        },
        'PyMES_Corporativo': {
            'name': 'Daños PyMES y Corporativo',
            'products': [
                'Negocio Protegido GNP', 'Cyber Safe',
                'Transporte de Mercancías', 'Responsabilidad Civil',
                'Condominios - Áreas Comunes', 
                'Responsabilidad Civil Profesional',
                'Equipo de Contratistas con RC', 'Equipo Electrónico',
                'Técnicos', 'Embarcaciones Menores de Placer',
                'Multirriesgo Protegido GNP', 
                'Responsabilidad Ambiental GNP',
                'Agricultura Protegida GNP'
            ]
        }
    }
}

def create_master_index():
    """Crear índice maestro con TODOS los productos"""
    
    logger.info("\n" + "="*80)
    logger.info("📝 CREANDO ÍNDICE MAESTRO DE PRODUCTOS GNP")
    logger.info("="*80 + "\n")
    
    doc_text = "CATÁLOGO COMPLETO DE PRODUCTOS GNP\n\n"
    doc_text += "GNP ofrece seguros en 4 áreas principales:\n\n"
    
    total_products = 0
    
    for area, segments in GNP_PRODUCTS.items():
        doc_text += f"{'='*60}\n"
        doc_text += f"{area.upper()}\n"
        doc_text += f"{'='*60}\n\n"
        
        for segment, info in segments.items():
            segment_name = segment.replace('_', ' ')
            doc_text += f"► {info['name']}\n\n"
            
            # Manejar estructura plana vs anidada (Vida tiene subcategorías)
            if isinstance(info['products'], dict):
                # Vida Individual tiene subcategorías
                for subcat, prods in info['products'].items():
                    doc_text += f"  {subcat}:\n"
                    for prod in prods:
                        doc_text += f"    • {prod}\n"
                        total_products += 1
                    doc_text += "\n"
            else:
                # Estructura plana
                for prod in info['products']:
                    doc_text += f"  • {prod}\n"
                    total_products += 1
                doc_text += "\n"
        
        doc_text += "\n"
    
    doc_text += f"\nTOTAL DE PRODUCTOS: {total_products}\n\n"
    doc_text += "Para información específica sobre cualquier producto, "
    doc_text += "consulta al chatbot mencionando el nombre del producto.\n"
    
    logger.info(f"✅ Índice maestro creado")
    logger.info(f"   Total productos: {total_products}")
    logger.info(f"   Tamaño: {len(doc_text)} caracteres\n")
    
    return doc_text, total_products

def create_area_index(area, segments):
    """Crear índice específico por área"""
    
    logger.info(f"📝 Creando índice de {area}...")
    
    doc_text = f"PRODUCTOS DE {area.upper()} - GNP\n\n"
    
    for segment, info in segments.items():
        doc_text += f"{info['name']}\n"
        doc_text += "-" * len(info['name']) + "\n\n"
        
        if isinstance(info['products'], dict):
            # Con subcategorías (Vida)
            for subcat, prods in info['products'].items():
                doc_text += f"{subcat}:\n"
                for prod in prods:
                    doc_text += f"• {prod}\n"
                doc_text += "\n"
        else:
            # Sin subcategorías
            for prod in info['products']:
                doc_text += f"• {prod}\n"
            doc_text += "\n"
    
    doc_text += f"\nEstos productos de {area} están diseñados para diferentes "
    doc_text += "necesidades, tanto para personas físicas (Individual) como "
    doc_text += "para empresas (PyMES y Corporativo).\n"
    
    logger.info(f"   ✅ Tamaño: {len(doc_text)} caracteres\n")
    
    return doc_text

def upload_synthetic_doc(doc_id, doc_text, category, doc_type='master'):
    """Subir documento sintético a Pinecone"""
    
    try:
        # Generar embedding
        embedding = embedding_service.generate_embedding(doc_text)
        
        # Metadata
        metadata = {
            'text': doc_text,
            'source': f'Índice Oficial {category}',
            'blobType': 'synthetic/official-index',
            'line': 0.0,
            'loc.lines.from': 0.0,
            'loc.lines.to': 0.0,
            'doc_type': f'synthetic_{doc_type}_index',
            'category': category.lower()
        }
        
        # Subir
        pinecone_service.upsert_vectors([(doc_id, embedding, metadata)])
        
        logger.info(f"   ✅ Subido: {doc_id}")
        return True
        
    except Exception as e:
        logger.error(f"   ❌ Error: {e}")
        return False

def main():
    """Proceso principal"""
    
    logger.info("\n" + "="*80)
    logger.info("🚀 CREACIÓN DE ÍNDICES SINTÉTICOS CON PRODUCTOS REALES")
    logger.info("="*80 + "\n")
    
    results = []
    
    # 1. Crear y subir índice maestro
    logger.info("PASO 1: Índice Maestro (todos los productos)\n")
    master_text, total = create_master_index()
    
    success = upload_synthetic_doc(
        'synthetic-master-catalog',
        master_text,
        'Catálogo General',
        'master'
    )
    results.append(('Índice Maestro', success, total))
    
    # 2. Crear índices por área
    logger.info("\nPASO 2: Índices por área\n")
    
    for area, segments in GNP_PRODUCTS.items():
        area_text = create_area_index(area, segments)
        
        # Normalizar área para ASCII (sin ñ ni acentos)
        area_ascii = area.lower().replace('ñ', 'n').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        doc_id = f'synthetic-area-{area_ascii}'
        success = upload_synthetic_doc(
            doc_id,
            area_text,
            area,
            'area'
        )
        
        # Contar productos
        prod_count = 0
        for seg_info in segments.values():
            if isinstance(seg_info['products'], dict):
                for prods in seg_info['products'].values():
                    prod_count += len(prods)
            else:
                prod_count += len(seg_info['products'])
        
        results.append((area, success, prod_count))
    
    # Resumen final
    logger.info("\n" + "="*80)
    logger.info("📊 RESUMEN FINAL")
    logger.info("="*80 + "\n")
    
    success_count = sum(1 for _, s, _ in results if s)
    total_docs = len(results)
    
    logger.info(f"Documentos creados: {success_count}/{total_docs}\n")
    
    for name, success, count in results:
        status = "✅" if success else "❌"
        logger.info(f"{status} {name}: {count} productos")
    
    if success_count == total_docs:
        logger.info("\n" + "="*80)
        logger.info("🎉 PROCESO COMPLETADO EXITOSAMENTE")
        logger.info("="*80 + "\n")
        logger.info("💡 El chatbot ahora puede responder preguntas como:\n")
        logger.info("   📋 Generales:")
        logger.info("      • ¿Qué productos tiene GNP?")
        logger.info("      • Lista todos los seguros")
        logger.info("      • ¿Cuántos productos ofrecen?\n")
        logger.info("   🎯 Por área:")
        logger.info("      • ¿Qué productos de Vida tienen?")
        logger.info("      • Lista los seguros de Autos")
        logger.info("      • ¿Cuáles son los productos de GMM?\n")
        logger.info("   🏢 Por segmento:")
        logger.info("      • Productos de Vida Individual")
        logger.info("      • Seguros para PyMES")
        logger.info("      • ¿Qué tienen para empresas?\n")
        logger.info("   🔍 Específicas:")
        logger.info("      • ¿Qué es Visión Plus?")
        logger.info("      • Diferencia entre Platino y Premium")
        logger.info("      • ¿Cuáles son los planes internacionales?\n")
    else:
        logger.warning("\n⚠️  Algunos documentos fallaron. Revisa los logs.")

if __name__ == "__main__":
    main()
