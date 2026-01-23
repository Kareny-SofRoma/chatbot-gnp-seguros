"""
Script para limpiar el caché de Redis

Limpia completamente el caché de Redis para forzar la regeneración
de respuestas con los documentos actualizados.

Uso:
    python backend/scripts/clear_redis_cache.py
"""

import sys
from pathlib import Path
import redis

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger()

def main():
    """Script principal"""
    
    print("=" * 80)
    print("LIMPIEZA DE CACHÉ DE REDIS")
    print("=" * 80)
    
    try:
        # Conectar a Redis
        redis_client = redis.from_url(settings.REDIS_URL)
        
        # Limpiar todo el caché
        redis_client.flushdb()
        
        print("\n✅ Caché de Redis limpiado exitosamente")
        print("\n📝 Todas las consultas futuras generarán respuestas nuevas")
        print("   usando los documentos más recientes de Pinecone")
        
        print("\n" + "=" * 80)
        print("✅ LIMPIEZA COMPLETADA")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error limpiando caché de Redis: {str(e)}")
        logger.error(f"Error en clear_redis_cache: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
