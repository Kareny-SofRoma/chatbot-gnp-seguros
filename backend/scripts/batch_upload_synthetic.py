"""
Uploader batch de documentos sintéticos a Pinecone

Este script sube automáticamente todos los documentos sintéticos
generados a Pinecone.

Uso:
    python backend/scripts/batch_upload_synthetic.py
"""

import sys
import os
from pathlib import Path
import hashlib
from datetime import datetime
import unicodedata
import re

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.embedding_service import embedding_service
from app.services.pinecone_service import pinecone_service
from app.core.logger import get_logger

logger = get_logger()

def normalize_for_id(text: str) -> str:
    """Normaliza texto para usar en IDs de Pinecone (solo ASCII)"""
    # Normalizar unicode (descomponer acentos)
    nfkd = unicodedata.normalize('NFKD', text)
    # Remover marcas diacríticas y convertir a ASCII
    ascii_text = nfkd.encode('ASCII', 'ignore').decode('ASCII')
    # Reemplazar espacios con guiones bajos
    ascii_text = ascii_text.replace(' ', '_')
    # Remover cualquier caracter que no sea alfanumérico, guión bajo o guión
    ascii_text = re.sub(r'[^a-zA-Z0-9_-]', '', ascii_text)
    return ascii_text.lower()

def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 200) -> list:
    """Divide texto en chunks con overlap"""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        if end < len(text):
            search_area = text[end-200:end]
            last_newline = search_area.rfind('\n')
            last_period = search_area.rfind('. ')
            
            if last_newline > 0:
                end = end - 200 + last_newline
            elif last_period > 0:
                end = end - 200 + last_period + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap if end < len(text) else end
    
    return chunks

def upload_synthetic_document(filepath: Path):
    """Sube un documento sintético a Pinecone"""
    
    # Leer archivo
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not content.strip():
        print(f"   ⚠️  Archivo vacío, saltando")
        return None
    
    # Extraer producto y categoría del nombre del archivo
    # Formato esperado: synthetic_producto_categoria.txt
    filename = filepath.stem
    parts = filename.split('_')
    
    if len(parts) >= 3 and parts[0] == 'synthetic':
        product = parts[1]
        category = '_'.join(parts[2:])
    else:
        product = "unknown"
        category = "general"
    
    print(f"   📦 Producto: {product}")
    print(f"   🏷️  Categoría: {category}")
    print(f"   📏 Tamaño: {len(content)} caracteres")
    
    # Dividir en chunks
    chunks = chunk_text(content, chunk_size=2000, overlap=200)
    print(f"   ✂️  Dividido en {len(chunks)} chunks")
    
    # Generar embeddings
    print(f"   🔄 Generando embeddings...")
    try:
        embeddings = embedding_service.generate_embeddings_batch(chunks)
        print(f"   ✅ {len(embeddings)} embeddings generados")
    except Exception as e:
        print(f"   ❌ Error generando embeddings: {str(e)}")
        return None
    
    # Preparar vectores
    timestamp = datetime.now().isoformat()
    vectors = []
    
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        chunk_hash = hashlib.md5(chunk.encode()).hexdigest()[:8]
        # Normalizar producto y categoría para IDs (ASCII-only)
        product_id = normalize_for_id(product)
        category_id = normalize_for_id(category)
        vector_id = f"synthetic_{product_id}_{category_id}_{chunk_hash}_{i}"
        
        vectors.append({
            "id": vector_id,
            "values": embedding,
            "metadata": {
                "text": chunk,
                "source": filepath.name,
                "doc_type": "synthetic",
                "product": product,
                "category": category,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "uploaded_at": timestamp
            }
        })
    
    # Subir a Pinecone
    print(f"   ⬆️  Subiendo {len(vectors)} vectores...")
    
    try:
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i+batch_size]
            pinecone_service.upsert_vectors(batch)
        
        print(f"   ✅ Subido exitosamente")
        
        return {
            'product': product,
            'category': category,
            'chunks': len(chunks),
            'vectors': len(vectors)
        }
        
    except Exception as e:
        print(f"   ❌ Error subiendo a Pinecone: {str(e)}")
        return None

def main():
    """Script principal"""
    
    print("=" * 80)
    print("UPLOADER BATCH DE DOCUMENTOS SINTÉTICOS")
    print("=" * 80)
    
    # Lista de archivos que fallaron en la ejecución anterior (con caracteres especiales)
    failed_files = [
        "synthetic_conexión gnp_coaseguros.txt",
        "synthetic_conexión gnp_deducibles.txt",
        "synthetic_versátil_coaseguros.txt",
        "synthetic_versátil_deducibles.txt",
        "synthetic_versátil_requisitos.txt",
        "synthetic_versátil_sumas_aseguradas.txt",
        "synthetic_versátil_exclusiones.txt",
        "synthetic_conexión gnp_sumas_aseguradas.txt",
        "synthetic_versátil_periodos_espera.txt",
        "synthetic_conexión gnp_indemnizaciones.txt",
        "synthetic_conexión gnp_coberturas.txt",
        "synthetic_versátil_indemnizaciones.txt",
        "synthetic_conexión gnp_exclusiones.txt",
        "synthetic_versátil_coberturas.txt",
        "synthetic_conexión gnp_periodos_espera.txt"
    ]
    
    # Directorio de documentos sintéticos
    synthetic_dir = Path("data/synthetic")
    
    if not synthetic_dir.exists():
        print(f"\n❌ Directorio no existe: {synthetic_dir}")
        print("\n💡 Primero ejecuta: python backend/scripts/generate_synthetic_docs.py")
        return
    
    # Filtrar solo los archivos que fallaron
    synthetic_files = []
    for filename in failed_files:
        filepath = synthetic_dir / filename
        if filepath.exists():
            synthetic_files.append(filepath)
        else:
            print(f"⚠️  Archivo no encontrado: {filename}")
    
    if not synthetic_files:
        print(f"\n❌ No se encontraron archivos que fallaron en: {synthetic_dir}")
        return
    
    print(f"\n📁 Procesando SOLO los {len(synthetic_files)} archivos que fallaron previamente")
    print("📝 (Archivos con caracteres especiales: ó, á)\n")
    
    # Subir cada documento
    results = []
    
    for i, filepath in enumerate(synthetic_files, 1):
        print(f"\n{'='*80}")
        print(f"[{i}/{len(synthetic_files)}] Procesando: {filepath.name}")
        print(f"{'='*80}")
        
        result = upload_synthetic_document(filepath)
        if result:
            results.append(result)
    
    # Resumen
    print("\n" + "=" * 80)
    print("PROCESO COMPLETADO")
    print("=" * 80)
    
    print(f"\n✅ {len(results)}/{len(synthetic_files)} documentos subidos exitosamente\n")
    
    # Estadísticas
    total_vectors = sum(r['vectors'] for r in results)
    
    print("📊 ESTADÍSTICAS:")
    print(f"   Total vectores subidos: {total_vectors}")
    print(f"   Productos únicos: {len(set(r['product'] for r in results))}")
    print(f"   Categorías únicas: {len(set(r['category'] for r in results))}")
    
    print("\n📋 DETALLE POR DOCUMENTO:")
    for r in results:
        print(f"   • {r['product']} - {r['category']}: {r['vectors']} vectores")
    
    print(f"\n🎉 Los documentos sintéticos están ahora disponibles en Pinecone")
    print(f"   con prioridad máxima en las búsquedas (doc_type='synthetic')")

if __name__ == "__main__":
    main()
