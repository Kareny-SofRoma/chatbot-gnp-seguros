from app.services.embedding_service import embedding_service
from app.services.pinecone_service import pinecone_service
from app.services.llm_service import llm_service
from app.core.redis_client import get_redis
from app.core.logger import get_logger
from typing import List, Dict, Tuple
import json
import hashlib
import time

logger = get_logger()

class RAGService:
    def __init__(self):
        self.embedding_service = embedding_service
        self.pinecone_service = pinecone_service
        self.llm_service = llm_service
        self.redis = get_redis()
        self.cache_ttl = 86400  # 24 horas (queries similares son comunes)
    
    def query(
        self,
        user_query: str,
        conversation_history: List[Dict] = None,
        top_k: int = 25  # Más resultados para mejor cobertura
    ) -> Tuple[str, List[Dict], int]:
        """
        Optimized RAG query with aggressive caching
        """
        start_time = time.time()
        
        try:
            # Check cache FIRST (fastest path)
            cache_key = self._generate_cache_key(user_query)
            cached_response = self._get_from_cache(cache_key)
            if cached_response:
                elapsed = (time.time() - start_time) * 1000
                logger.info(f"⚡ Cache HIT - Response in {elapsed:.0f}ms")
                return cached_response
            
            logger.info(f"Processing query: {user_query[:100]}...")
            
            # Query expansion para mejor recall
            search_queries = self._expand_query(user_query)
            logger.info(f"Expanded to {len(search_queries)} queries")
            
            # Búsqueda paralela (simular con secuencial por ahora)
            all_chunks = []
            seen_ids = set()
            
            for sq in search_queries:
                query_embedding = self.embedding_service.generate_embedding(sq)
                
                results = self.pinecone_service.query_vectors(
                    query_vector=query_embedding,
                    top_k=15  # 15 por query
                )
                
                for match in results.matches:
                    if match.id not in seen_ids and match.score > 0.45:  # Threshold más bajo
                        seen_ids.add(match.id)
                        all_chunks.append({
                            'id': match.id,
                            'text': match.metadata.get('text', ''),
                            'score': match.score,
                            'source': match.metadata.get('source', 'Manual GNP'),
                            'doc_type': match.metadata.get('doc_type', 'pdf')
                        })
            
            # Priorizar documentos sintéticos (tienen info consolidada)
            all_chunks.sort(key=lambda x: (
                1 if 'synthetic' in x['doc_type'] else 0,  # Sintéticos primero
                x['score']  # Luego por score
            ), reverse=True)
            
            # Tomar top chunks
            top_chunks = all_chunks[:20]  # Top 20 mejores
            
            if not top_chunks:
                logger.warning("No relevant chunks found")
                return "Lo siento, no encontré información sobre esa pregunta en los manuales de GNP.", [], 0
            
            # Construir contexto
            context_text = "\n\n---\n\n".join([c['text'] for c in top_chunks])
            
            logger.info(f"Found {len(top_chunks)} chunks (best: {top_chunks[0]['score']:.3f})")
            logger.info(f"Context size: {len(context_text)} chars")
            
            # Generar respuesta
            response, tokens_used = self.llm_service.generate_response(
                user_message=user_query,
                context=context_text,
                conversation_history=conversation_history
            )
            
            # Preparar sources
            sources = [{
                'source': c['source'],
                'score': round(c['score'], 3),
                'text_preview': c['text'][:200] + '...' if len(c['text']) > 200 else c['text']
            } for c in top_chunks[:10]]  # Top 10 sources
            
            # Cache agresivo
            result = (response, sources, tokens_used)
            self._save_to_cache(cache_key, result)
            
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"⚡ Total time: {elapsed:.0f}ms")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in RAG query: {str(e)}")
            raise
    
    def _expand_query(self, query: str) -> List[str]:
        """Smart query expansion"""
        query_lower = query.lower()
        expansions = [query]
        
        # Detectar tipo de pregunta
        if any(word in query_lower for word in ['todos', 'lista', 'cuáles', 'qué productos']):
            # Pregunta de listado
            expansions.extend([
                "catálogo productos GNP seguros",
                "lista completa seguros GNP",
                f"{query} completo"
            ])
        
        elif 'internacional' in query_lower:
            expansions.extend([
                "planes internacionales GMM",
                "cobertura internacional GNP",
                "Enlace Vínculo Mundial"
            ])
        
        elif any(word in query_lower for word in ['requisitos', 'cómo', 'proceso', 'pasos']):
            # Pregunta de procedimiento
            expansions.extend([
                f"{query} procedimiento",
                f"{query} documentos necesarios"
            ])
        
        elif any(word in query_lower for word in ['qué es', 'define', 'significa']):
            # Pregunta de definición
            expansions.append(f"definición {query.replace('qué es', '').replace('?', '')}")
        
        return expansions[:3]  # Max 3 queries
    
    def _generate_cache_key(self, query: str) -> str:
        """Generate cache key"""
        normalized = query.lower().strip()
        query_hash = hashlib.md5(normalized.encode()).hexdigest()
        return f"rag:v2:{query_hash}"  # v2 para nueva versión
    
    def _get_from_cache(self, cache_key: str):
        """Get from cache"""
        try:
            cached = self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache get error: {str(e)}")
        return None
    
    def _save_to_cache(self, cache_key: str, result):
        """Save to cache"""
        try:
            self.redis.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(result)
            )
        except Exception as e:
            logger.warning(f"Cache save error: {str(e)}")

rag_service = RAGService()
