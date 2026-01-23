"""
Script para listar todos los productos disponibles en Pinecone

Analiza todos los vectores y extrae los productos únicos con su conteo.

Uso:
    python backend/scripts/list_products.py
"""

import sys
from pathlib import Path
from collections import Counter

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.pinecone_service import pinecone_service
from app.core.logger import get_logger

logger = get_logger()

def main():
    """Script principal"""
    
    print("=" * 80)
    print("PRODUCTOS DISPONIBLES EN PINECONE")
    print("=" * 80)
    
    try:
        index = pinecone_service.get_index()
        
        # Query con vector dummy para obtener muestras
        print("\n🔍 Analizando vectores en Pinecone...")
        
        # Obtener muestra de todos los vectores
        results = index.query(
            vector=[0.0] * 3072,
            top_k=10000,
            include_metadata=True
        )
        
        print(f"\n📊 Muestra analizada: {len(results.matches)} vectores")
        
        # Contar productos
        products = []
        doc_types = []
        
        for match in results.matches:
            metadata = match.metadata
            product = metadata.get('product', 'sin_producto')
            doc_type = metadata.get('doc_type', 'sin_tipo')
            
            products.append(product)
            doc_types.append(doc_type)
        
        # Estadísticas
        product_counts = Counter(products)
        doc_type_counts = Counter(doc_types)
        
        print("\n" + "=" * 80)
        print("📦 PRODUCTOS ENCONTRADOS:")
        print("=" * 80)
        
        for product, count in sorted(product_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {product}: {count:,} vectores")
        
        print("\n" + "=" * 80)
        print("📝 TIPOS DE DOCUMENTOS:")
        print("=" * 80)
        
        for doc_type, count in sorted(doc_type_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {doc_type}: {count:,} vectores")
        
        print("\n" + "=" * 80)
        print("✅ ANÁLISIS COMPLETADO")
        print("=" * 80)
        
        # Recomendaciones
        print("\n💡 RECOMENDACIONES:")
        if 'sin_producto' in product_counts:
            print(f"   ⚠️  Hay {product_counts['sin_producto']:,} vectores sin campo 'product'")
            print("   → Estos vectores no aparecerán en búsquedas por producto")
        
        synthetic_count = doc_type_counts.get('synthetic', 0)
        manual_count = doc_type_counts.get('manual', 0)
        
        print(f"\n   📝 Documentos sintéticos: {synthetic_count}")
        print(f"   📄 Documentos de manuales: {manual_count}")
        
        if manual_count == 0:
            print("   ⚠️  No se encontraron documentos con doc_type='manual'")
            print("   → Revisa si los manuales originales tienen este campo")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.error(f"Error en list_products: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
