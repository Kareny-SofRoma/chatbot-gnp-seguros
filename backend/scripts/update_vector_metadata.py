"""
Script para actualizar metadata de vectores existentes en Pinecone

Este script agrega los campos 'product', 'area' y 'doc_type' a vectores que no los tienen,
extrayendo el producto y área del nombre del archivo o contenido.

Uso:
    python backend/scripts/update_vector_metadata.py
"""

import sys
import re
from pathlib import Path
from typing import Dict, Optional, Tuple
import time

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.pinecone_service import pinecone_service
from app.core.logger import get_logger

logger = get_logger()

# Mapeo de patrones de productos conocidos con sus áreas
PRODUCT_PATTERNS = {
    # GMM - Gastos Médicos Mayores
    'premium': {
        'patterns': ['premium', 'prémium'],
        'area': 'gmm'
    },
    'conexión gnp': {
        'patterns': ['conexion', 'conexión', 'conexion gnp', 'conexión gnp'],
        'area': 'gmm'
    },
    'versátil': {
        'patterns': ['versatil', 'versátil'],
        'area': 'gmm'
    },
    'alta especialidad': {
        'patterns': ['alta especialidad', 'altaespecialidad', 'alta_especialidad'],
        'area': 'gmm'
    },
    'línea azul vip': {
        'patterns': ['linea azul vip', 'línea azul vip', 'lineaazulvip', 'vip'],
        'area': 'gmm'
    },
    'línea azul': {
        'patterns': ['linea azul', 'línea azul', 'lineaazul'],
        'area': 'gmm'
    },
    'vip internacional': {
        'patterns': ['vip internacional', 'vipinternacional'],
        'area': 'gmm'
    },
    'enlace internacional': {
        'patterns': ['enlace internacional', 'enlaceinternacional'],
        'area': 'gmm'
    },
    'vínculo mundial': {
        'patterns': ['vinculo mundial', 'vínculo mundial', 'vinculomundial'],
        'area': 'gmm'
    },
    'personaliza': {
        'patterns': ['personaliza'],
        'area': 'gmm'
    },
    'flexibles': {
        'patterns': ['flexibles', 'flexible'],
        'area': 'gmm'
    },
    'acceso': {
        'patterns': ['acceso'],
        'area': 'gmm'
    },
    'esencial': {
        'patterns': ['esencial'],
        'area': 'gmm'
    },
    'plenitud': {
        'patterns': ['plenitud'],
        'area': 'gmm'
    },
    'platino': {
        'patterns': ['platino'],
        'area': 'gmm'
    },
    'gnp indemniza': {
        'patterns': ['gnp indemniza', 'indemniza'],
        'area': 'gmm'
    },
}

# Patrones para detectar áreas en nombres de archivo
AREA_PATTERNS = {
    'gmm': ['gmm', 'gastos medicos', 'gastos médicos', 'medico', 'médico', 'salud'],
    'vida': ['vida', 'fallecimiento', 'sobrevivencia'],
    'autos': ['autos', 'auto', 'vehiculo', 'vehículo', 'automovil', 'automóvil'],
    'daños': ['daños', 'danos', 'hogar', 'empresarial', 'incendio', 'terremoto']
}

def normalize_text(text: str) -> str:
    """Normaliza texto para comparación"""
    text = text.lower()
    # Remover acentos
    text = text.replace('á', 'a').replace('é', 'e').replace('í', 'i')
    text = text.replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')
    # Remover caracteres especiales
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text.strip()

def extract_product_from_text(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Extrae el nombre del producto y área del texto usando patrones conocidos
    Returns: (product_name, area)
    """
    normalized = normalize_text(text)
    
    # Buscar coincidencias con patrones conocidos
    for product, config in PRODUCT_PATTERNS.items():
        for pattern in config['patterns']:
            pattern_normalized = normalize_text(pattern)
            if pattern_normalized in normalized:
                return product, config['area']
    
    return None, None

def extract_area_from_text(text: str) -> Optional[str]:
    """Extrae el área del texto usando patrones conocidos"""
    normalized = normalize_text(text)
    
    # Buscar coincidencias con patrones de áreas
    for area, patterns in AREA_PATTERNS.items():
        for pattern in patterns:
            pattern_normalized = normalize_text(pattern)
            if pattern_normalized in normalized:
                return area
    
    return None

def extract_product_from_source(source: str) -> Tuple[Optional[str], Optional[str]]:
    """Extrae el producto y área del nombre del archivo source
    Returns: (product_name, area)
    """
    # Remover extensión y números al inicio
    filename = source.lower()
    filename = re.sub(r'\.pdf$', '', filename)
    filename = re.sub(r'^\d+[\s_-]*', '', filename)  # Remover números al inicio
    
    # Intentar extraer producto y área
    product, area = extract_product_from_text(filename)
    
    # Si no se encontró área en el producto, buscar en el filename completo
    if not area:
        area = extract_area_from_text(filename)
    
    return product, area

def get_vectors_batch(index, batch_size: int = 10000):
    """Obtiene un batch de vectores del índice"""
    try:
        results = index.query(
            vector=[0.0] * 3072,
            top_k=batch_size,
            include_metadata=True
        )
        return results.matches
    except Exception as e:
        logger.error(f"Error obteniendo vectores: {str(e)}")
        return []

def update_vector_metadata(index, vector_id: str, metadata: Dict):
    """Actualiza la metadata de un vector"""
    try:
        # Pinecone requiere el vector completo para actualizar
        # Usamos fetch para obtener el vector actual
        fetch_result = index.fetch(ids=[vector_id])
        
        if vector_id not in fetch_result.vectors:
            logger.warning(f"Vector {vector_id} no encontrado")
            return False
        
        vector_data = fetch_result.vectors[vector_id]
        
        # Actualizar metadata manteniendo los valores existentes
        updated_metadata = vector_data.metadata.copy()
        updated_metadata.update(metadata)
        
        # Upsert con nueva metadata
        index.upsert(vectors=[{
            'id': vector_id,
            'values': vector_data.values,
            'metadata': updated_metadata
        }])
        
        return True
        
    except Exception as e:
        logger.error(f"Error actualizando vector {vector_id}: {str(e)}")
        return False

def main():
    """Script principal"""
    
    print("=" * 80)
    print("ACTUALIZACIÓN DE METADATA DE VECTORES")
    print("=" * 80)
    
    print("\n📋 Este script agregará los campos 'product', 'area' y 'doc_type'")
    print("   a vectores existentes que no los tienen.\n")
    
    # Confirmar
    response = input("¿Deseas continuar? (sí/no): ").strip().lower()
    if response not in ['si', 'sí', 's', 'yes', 'y']:
        print("\n❌ Operación cancelada")
        return
    
    try:
        index = pinecone_service.get_index()
        
        print("\n🔍 Obteniendo vectores sin metadata completa...")
        
        # Obtener vectores
        vectors = get_vectors_batch(index, batch_size=10000)
        print(f"   📊 Muestra obtenida: {len(vectors)} vectores")
        
        # Filtrar vectores sin doc_type (el campo más importante)
        vectors_to_update = []
        
        for vector in vectors:
            metadata = vector.metadata
            # Solo actualizar si NO tiene doc_type
            # Los campos product y area son opcionales
            has_doc_type = 'doc_type' in metadata and metadata['doc_type'] not in ['', 'sin_tipo']
            
            if not has_doc_type:
                vectors_to_update.append(vector)
        
        print(f"   ✅ Vectores que necesitan actualización: {len(vectors_to_update)}")
        
        if len(vectors_to_update) == 0:
            print("\n✅ No hay vectores para actualizar")
            return
        
        # Estadísticas
        products_found = {}
        areas_found = {}
        products_not_found = 0
        areas_not_found = 0
        updated_count = 0
        error_count = 0
        
        print("\n🔄 Actualizando metadata...")
        print(f"   Esto puede tomar varios minutos...\n")
        
        for i, vector in enumerate(vectors_to_update, 1):
            vector_id = vector.id
            metadata = vector.metadata
            
            # Intentar extraer producto y área del source
            source = metadata.get('source', '')
            text = metadata.get('text', '')
            
            # Si el source es "blob", buscar directamente en el texto (más extenso)
            if source == 'blob' or not source:
                # Analizar más texto para archivos sin nombre (hasta 500 chars)
                product, area = extract_product_from_text(text[:500])
            else:
                # Si hay nombre de archivo, usar ese primero
                product, area = extract_product_from_source(source)
                
                # Si no se encuentra en source, intentar en text (primeras 200 chars)
                if not product and text:
                    product, area = extract_product_from_text(text[:200])
            
            # Si aún no hay área, intentar buscarla en el texto completo
            if not area and text:
                area = extract_area_from_text(text[:500])
            
            # Preparar metadata actualizada
            new_metadata = {}
            
            if product:
                new_metadata['product'] = product
                products_found[product] = products_found.get(product, 0) + 1
            else:
                new_metadata['product'] = 'unknown'
                products_not_found += 1
            
            if area:
                new_metadata['area'] = area
                areas_found[area] = areas_found.get(area, 0) + 1
            else:
                new_metadata['area'] = 'unknown'
                areas_not_found += 1
            
            # Agregar doc_type si no existe
            if 'doc_type' not in metadata:
                new_metadata['doc_type'] = 'manual'
            
            # Actualizar vector
            success = update_vector_metadata(index, vector_id, new_metadata)
            
            if success:
                updated_count += 1
            else:
                error_count += 1
            
            # Progreso
            if i % 100 == 0:
                print(f"   Procesados: {i}/{len(vectors_to_update)} vectores...")
                time.sleep(0.1)  # Pequeña pausa para no saturar
        
        # Resumen
        print("\n" + "=" * 80)
        print("RESUMEN DE ACTUALIZACIÓN")
        print("=" * 80)
        
        print(f"\n✅ Vectores actualizados exitosamente: {updated_count:,}")
        print(f"❌ Errores: {error_count:,}")
        
        print("\n📦 PRODUCTOS IDENTIFICADOS:")
        for product, count in sorted(products_found.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {product}: {count:,} vectores")
        
        print("\n🏢 ÁREAS IDENTIFICADAS:")
        for area, count in sorted(areas_found.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {area}: {count:,} vectores")
        
        if products_not_found > 0:
            print(f"\n⚠️  Vectores sin producto identificable: {products_not_found:,}")
            print("   → Estos se marcaron como 'unknown'")
        
        if areas_not_found > 0:
            print(f"\n⚠️  Vectores sin área identificable: {areas_not_found:,}")
            print("   → Estos se marcaron como 'unknown'")
        
        print("\n" + "=" * 80)
        print("✅ ACTUALIZACIÓN COMPLETADA")
        print("=" * 80)
        
        print("\n💡 SIGUIENTE PASO:")
        print("   Ejecuta este script varias veces más hasta procesar todos los ~63K vectores")
        print("   Luego: python scripts/clear_redis_cache.py")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.error(f"Error en update_vector_metadata: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
