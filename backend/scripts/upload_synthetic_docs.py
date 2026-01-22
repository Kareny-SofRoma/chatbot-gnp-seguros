"""
Script para subir documentos sintéticos a Pinecone

Este script permite subir documentos consolidados (sintéticos) a Pinecone
para mejorar la recuperación de información fragmentada.

Uso:
    python backend/scripts/upload_synthetic_docs.py

Ejemplo para crear documento sintético:
    1. Identifica información fragmentada (ej: periodos de espera)
    2. Crea archivo .txt en backend/data/ con TODO el contenido consolidado
    3. Ejecuta este script
"""

import sys
import os
from pathlib import Path
import hashlib
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.embedding_service import embedding_service
from app.services.pinecone_service import pinecone_service
from app.core.logger import get_logger

logger = get_logger()

def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 200) -> list:
    """
    Divide texto en chunks con overlap
    
    Para documentos sintéticos, usamos chunks más grandes (2000 chars)
    porque queremos mantener la información consolidada.
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Si no es el último chunk, buscar un punto de corte natural
        if end < len(text):
            # Buscar el último salto de línea o punto en los últimos 200 caracteres
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
        
        # Mover el inicio con overlap
        start = end - overlap if end < len(text) else end
    
    return chunks

def upload_synthetic_document(
    filepath: str,
    doc_name: str = None,
    product: str = "unknown",
    category: str = "synthetic"
):
    """
    Sube un documento sintético a Pinecone
    
    Args:
        filepath: Ruta al archivo .txt
        doc_name: Nombre del documento (opcional, se genera automáticamente)
        product: Nombre del producto (ej: "versatil", "premium")
        category: Categoría del documento (ej: "periodos_espera", "coberturas")
    """
    
    # Leer archivo
    print(f"\n📄 Leyendo archivo: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not content.strip():
        print("❌ El archivo está vacío")
        return
    
    # Generar nombre del documento si no se proporciona
    if not doc_name:
        doc_name = Path(filepath).stem
    
    print(f"📝 Documento: {doc_name}")
    print(f"📦 Producto: {product}")
    print(f"🏷️  Categoría: {category}")
    print(f"📏 Tamaño: {len(content)} caracteres")
    
    # Dividir en chunks
    chunks = chunk_text(content, chunk_size=2000, overlap=200)
    print(f"✂️  Dividido en {len(chunks)} chunks")
    
    # Generar embeddings
    print(f"\n🔄 Generando embeddings...")
    embeddings = embedding_service.generate_embeddings_batch(chunks)
    print(f"✅ {len(embeddings)} embeddings generados")
    
    # Preparar vectores para Pinecone
    timestamp = datetime.now().isoformat()
    vectors = []
    
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        # Generar ID único basado en el contenido
        chunk_hash = hashlib.md5(chunk.encode()).hexdigest()[:8]
        vector_id = f"synthetic_{product}_{category}_{chunk_hash}_{i}"
        
        vectors.append({
            "id": vector_id,
            "values": embedding,
            "metadata": {
                "text": chunk,
                "source": doc_name,
                "doc_type": "synthetic",
                "product": product,
                "category": category,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "uploaded_at": timestamp
            }
        })
    
    # Subir a Pinecone
    print(f"\n⬆️  Subiendo {len(vectors)} vectores a Pinecone...")
    
    try:
        # Subir en batches de 100
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i+batch_size]
            pinecone_service.upsert_vectors(batch)
            print(f"   ✓ Batch {i//batch_size + 1}/{(len(vectors)-1)//batch_size + 1} subido")
        
        print(f"\n✅ ÉXITO: {len(vectors)} vectores subidos a Pinecone")
        print(f"📊 Estadísticas:")
        print(f"   - Documento: {doc_name}")
        print(f"   - Chunks: {len(chunks)}")
        print(f"   - Producto: {product}")
        print(f"   - Categoría: {category}")
        print(f"   - IDs: synthetic_{product}_{category}_*")
        
    except Exception as e:
        print(f"\n❌ ERROR al subir a Pinecone: {str(e)}")
        raise

def main():
    """Script principal"""
    
    print("=" * 80)
    print("UPLOADER DE DOCUMENTOS SINTÉTICOS A PINECONE")
    print("=" * 80)
    
    # Archivo a subir (puedes cambiar esto)
    filepath = "data/synthetic_versatil_periodos_espera.txt"
    
    # Verificar que existe
    if not os.path.exists(filepath):
        print(f"\n❌ ERROR: Archivo no encontrado: {filepath}")
        print("\nAsegúrate de crear el archivo primero.")
        return
    
    # Subir documento
    upload_synthetic_document(
        filepath=filepath,
        doc_name="Periodos de Espera - Versátil (Consolidado)",
        product="versatil",
        category="periodos_espera"
    )
    
    print("\n" + "=" * 80)
    print("PROCESO COMPLETADO")
    print("=" * 80)
    
    print("""
💡 CÓMO CREAR MÁS DOCUMENTOS SINTÉTICOS:

1. IDENTIFICA información fragmentada en los PDFs
   Ejemplo: deducibles, coberturas, exclusiones de un producto

2. CREA archivo .txt en backend/data/ con nombre descriptivo
   Ejemplo: synthetic_premium_coberturas.txt

3. ESCRIBE el contenido consolidado en el archivo:
   - Título claro
   - Toda la información en un solo lugar
   - Estructura organizada con separadores (═══)
   - Incluye contexto del producto

4. MODIFICA este script (línea 153) con:
   - filepath: ruta al nuevo archivo
   - doc_name: nombre descriptivo
   - product: nombre del producto (ej: "premium", "platino")
   - category: categoría (ej: "coberturas", "deducibles")

5. EJECUTA: python backend/scripts/upload_synthetic_docs.py

IMPORTANTE:
- Los documentos sintéticos tienen prioridad en las búsquedas
- Usa chunks grandes (2000 chars) para mantener contexto
- Categoriza bien (product + category) para fácil identificación
""")

if __name__ == "__main__":
    main()
