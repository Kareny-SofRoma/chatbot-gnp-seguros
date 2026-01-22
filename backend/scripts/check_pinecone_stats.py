"""
Script para verificar estadísticas de Pinecone

Muestra información detallada sobre los vectores almacenados en Pinecone,
incluyendo totales, distribución por tipo de documento, productos y categorías.

Uso:
    python backend/scripts/check_pinecone_stats.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.pinecone_service import pinecone_service
from app.core.logger import get_logger

logger = get_logger()

def main():
    """Script principal"""
    
    print("=" * 80)
    print("ESTADÍSTICAS DE PINECONE")
    print("=" * 80)
    
    try:
        # Obtener el índice
        index = pinecone_service.get_index()
        
        # Obtener estadísticas del índice
        stats = index.describe_index_stats()
        
        print(f"\n📊 INFORMACIÓN GENERAL")
        print(f"   Total de vectores: {stats.total_vector_count:,}")
        print(f"   Dimensiones: {stats.dimension}")
        
        # Información por namespaces (si existen)
        if hasattr(stats, 'namespaces') and stats.namespaces:
            print(f"\n📁 NAMESPACES:")
            for namespace, ns_stats in stats.namespaces.items():
                ns_name = namespace if namespace else "(default)"
                print(f"   • {ns_name}: {ns_stats.vector_count:,} vectores")
        
        # Intentar obtener algunos vectores para análisis
        print(f"\n🔍 ANALIZANDO MUESTRA DE VECTORES...")
        
        # Query para obtener vectores sintéticos
        try:
            synthetic_results = index.query(
                vector=[0.0] * 3072,  # Vector dummy
                top_k=10000,
                include_metadata=True,
                filter={"doc_type": "synthetic"}
            )
            
            synthetic_count = len(synthetic_results.matches)
            print(f"\n📝 DOCUMENTOS SINTÉTICOS:")
            print(f"   Total: {synthetic_count} vectores")
            
            if synthetic_count > 0:
                # Contar por producto
                products = {}
                categories = {}
                
                for match in synthetic_results.matches:
                    metadata = match.metadata
                    product = metadata.get('product', 'unknown')
                    category = metadata.get('category', 'unknown')
                    
                    products[product] = products.get(product, 0) + 1
                    categories[category] = categories.get(category, 0) + 1
                
                print(f"\n   Por producto:")
                for product, count in sorted(products.items()):
                    print(f"      • {product}: {count} vectores")
                
                print(f"\n   Por categoría:")
                for category, count in sorted(categories.items()):
                    print(f"      • {category}: {count} vectores")
        
        except Exception as e:
            print(f"\n⚠️  No se pudieron obtener detalles de documentos sintéticos: {str(e)}")
        
        # Query para obtener vectores regulares
        try:
            regular_results = index.query(
                vector=[0.0] * 3072,  # Vector dummy
                top_k=10000,
                include_metadata=True,
                filter={"doc_type": "manual"}
            )
            
            regular_count = len(regular_results.matches)
            print(f"\n📄 DOCUMENTOS DE MANUALES:")
            print(f"   Total: {regular_count} vectores")
            
            if regular_count > 0:
                # Contar por producto
                products = {}
                
                for match in regular_results.matches:
                    metadata = match.metadata
                    product = metadata.get('product', 'unknown')
                    products[product] = products.get(product, 0) + 1
                
                print(f"\n   Por producto:")
                for product, count in sorted(products.items()):
                    print(f"      • {product}: {count} vectores")
        
        except Exception as e:
            print(f"\n⚠️  No se pudieron obtener detalles de documentos de manuales: {str(e)}")
        
        print("\n" + "=" * 80)
        print("✅ ANÁLISIS COMPLETADO")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error obteniendo estadísticas: {str(e)}")
        logger.error(f"Error en check_pinecone_stats: {str(e)}")
        return

if __name__ == "__main__":
    main()
