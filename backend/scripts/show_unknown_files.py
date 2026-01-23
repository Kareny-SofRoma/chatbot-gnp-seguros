"""
Script para ver ejemplos de nombres de archivos unknown

Muestra ejemplos de nombres de archivos que no fueron clasificados
para poder agregar más patrones.

Uso:
    python backend/scripts/show_unknown_files.py
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
    print("EJEMPLOS DE ARCHIVOS UNKNOWN")
    print("=" * 80)
    
    try:
        index = pinecone_service.get_index()
        
        # Query para obtener vectores unknown
        results = index.query(
            vector=[0.0] * 3072,
            top_k=100,  # Obtener 100 ejemplos
            include_metadata=True,
            filter={"product": "unknown"}
        )
        
        print(f"\n📊 Encontrados {len(results.matches)} ejemplos de archivos 'unknown'\n")
        
        # Mostrar primeros 50 nombres de archivo únicos
        sources_seen = set()
        count = 0
        
        print("📝 NOMBRES DE ARCHIVO:")
        print("-" * 80)
        
        for match in results.matches:
            source = match.metadata.get('source', 'sin_source')
            
            if source not in sources_seen and count < 50:
                sources_seen.add(source)
                count += 1
                print(f"{count}. {source}")
        
        print("\n" + "=" * 80)
        print("✅ EJEMPLOS MOSTRADOS")
        print("=" * 80)
        
        print("\n💡 Con estos ejemplos podemos agregar más patrones al script")
        print("   de actualización para clasificar estos archivos correctamente.")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.error(f"Error en show_unknown_files: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
