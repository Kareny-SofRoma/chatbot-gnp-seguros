#!/usr/bin/env python3
"""
Script para agregar documentos sintéticos (índices) a Pinecone
Esto soluciona el problema de preguntas generales sin re-procesar PDFs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.embedding_service import embedding_service
from app.services.pinecone_service import pinecone_service
from app.core.logger import get_logger
import uuid

logger = get_logger()

# DOCUMENTOS SINTÉTICOS - Información consolidada
SYNTHETIC_DOCS = [
    {
        "id": "synthetic-productos-gmm-lista",
        "text": """PRODUCTOS DE GASTOS MÉDICOS MAYORES (GMM) DE GNP

GNP ofrece los siguientes productos de Gastos Médicos Mayores:

**Seguro Médico GNP Personaliza**
- Premium
- Platino

**Planes Flexibles**
- Versátil
- Conexión GNP
- Conexión Línea Azul

**Planes de Indemnización**
- GNP Indemniza

**Planes Básicos y Especializados**
- Acceso
- Esencial
- Plenitud
- VIP

**Planes Internacionales**
- GNP Enlace Internacional
- Vínculo Mundial
- Alta Especialidad

Cada producto tiene diferentes coberturas, deducibles y beneficios específicos según las necesidades del cliente.""",
        "metadata": {
            "source": "Índice de Productos GNP",
            "doc_type": "synthetic_index",
            "category": "productos_gmm"
        }
    },
    {
        "id": "synthetic-planes-internacionales",
        "text": """PLANES INTERNACIONALES DE GASTOS MÉDICOS MAYORES GNP

GNP ofrece tres planes internacionales principales:

**1. GNP Enlace Internacional**
Ideal para personas que viajan frecuentemente o viven en el extranjero por periodos cortos.
Características:
- Cobertura en México y en el extranjero
- Red de proveedores internacionales
- Atención médica de urgencia en cualquier país

**2. Vínculo Mundial**
Diseñado para personas que trabajan o estudian en el extranjero por periodos largos.
Características:
- Cobertura mundial amplia
- Acceso a hospitales de prestigio internacional
- Mayor suma asegurada
- Cobertura de especialidades médicas avanzadas

**3. Alta Especialidad**
Para personas que buscan la mejor atención médica a nivel mundial.
Características:
- Cobertura en los mejores hospitales del mundo
- Acceso a tratamientos de vanguardia
- Sin límite geográfico
- Suma asegurada más alta

Estos planes ofrecen beneficios adicionales como:
- Asistencia médica telefónica 24/7
- Coordinación de citas médicas en el extranjero
- Segunda opinión médica internacional
- Evacuación médica de emergencia""",
        "metadata": {
            "source": "Índice Planes Internacionales",
            "doc_type": "synthetic_index",
            "category": "planes_internacionales"
        }
    }
]

def add_synthetic_docs():
    """Agregar documentos sintéticos a Pinecone"""
    
    logger.info(f"\n{'='*80}")
    logger.info("📝 AGREGANDO DOCUMENTOS SINTÉTICOS A PINECONE")
    logger.info(f"{'='*80}\n")
    
    logger.info(f"Total de documentos a agregar: {len(SYNTHETIC_DOCS)}\n")
    
    vectors_to_upsert = []
    
    for doc in SYNTHETIC_DOCS:
        logger.info(f"⚙️  Procesando: {doc['id']}")
        
        # Generar embedding
        embedding = embedding_service.generate_embedding(doc['text'])
        
        # Preparar metadata compatible con n8n
        metadata = {
            'text': doc['text'],
            'source': doc['metadata']['source'],
            'blobType': 'synthetic/index',
            'line': 0.0,
            'loc.lines.from': 0.0,
            'loc.lines.to': 0.0,
            'doc_type': doc['metadata']['doc_type'],
            'category': doc['metadata']['category']
        }
        
        vectors_to_upsert.append((doc['id'], embedding, metadata))
        logger.info(f"   ✅ Embedding generado ({len(embedding)} dims)")
    
    logger.info(f"\n⬆️  Subiendo {len(vectors_to_upsert)} vectores a Pinecone...")
    
    try:
        pinecone_service.upsert_vectors(vectors_to_upsert)
        logger.info(f"\n{'='*80}")
        logger.info("✅ DOCUMENTOS SINTÉTICOS AGREGADOS EXITOSAMENTE")
        logger.info(f"{'='*80}\n")
        
        logger.info("📊 Resumen:")
        for doc in SYNTHETIC_DOCS:
            logger.info(f"   ✅ {doc['id']}")
            logger.info(f"      Chars: {len(doc['text'])}")
            logger.info(f"      Categoría: {doc['metadata']['category']}")
        
        logger.info(f"\n💡 Ahora el sistema podrá responder preguntas como:")
        logger.info("   • ¿Cuáles son los productos de GMM?")
        logger.info("   • ¿Qué planes internacionales hay?")
        logger.info("   • Dame una lista de todos los seguros de GNP")
        
    except Exception as e:
        logger.error(f"\n❌ ERROR al subir vectores:")
        logger.error(str(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_synthetic_docs()
