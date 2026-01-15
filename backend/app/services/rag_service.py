from app.services.embedding_service import embedding_service
from app.services.pinecone_service import pinecone_service
from app.services.llm_service import llm_service
from app.core.redis_client import get_redis
from app.core.logger import get_logger
from typing import List, Dict, Tuple
import json
import hashlib

logger = get_logger()

class RAGService:
    def __init__(self):
        self.embedding_service = embedding_service
        self.pinecone_service = pinecone_service
        self.llm_service = llm_service
        self.redis = get_redis()
        self.cache_ttl = 3600  # 1 hour
    
    def query(
        self,
        user_query: str,
        conversation_history: List[Dict] = None,
        top_k: int = 5
    ) -> Tuple[str, List[Dict], int]:
        """
        Main RAG query method
        Returns: (response, sources, tokens_used)
        """
        try:
            # Check cache first
            cache_key = self._generate_cache_key(user_query)
            cached_response = self._get_from_cache(cache_key)
            if cached_response:
                logger.info("Returning cached response")
                return cached_response
            
            # Generate embedding for query
            logger.info(f"Processing query: {user_query[:100]}...")
            query_embedding = self.embedding_service.generate_embedding(user_query)
            
            # Search in Pinecone
            search_results = self.pinecone_service.query_vectors(
                query_vector=query_embedding,
                top_k=top_k
            )
            
            # Extract context and sources
            context, sources = self._process_search_results(search_results)
            
            # Generate response with LLM
            response, tokens_used = self.llm_service.generate_response(
                user_message=user_query,
                context=context,
                conversation_history=conversation_history
            )
            
            # Cache the response
            result = (response, sources, tokens_used)
            self._save_to_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in RAG query: {str(e)}")
            raise
    
    def _process_search_results(self, results) -> Tuple[str, List[Dict]]:
        """Process Pinecone search results into context and sources"""
        contexts = []
        sources = []
        
        for match in results.matches:
            metadata = match.metadata
            score = match.score
            
            # Only include high-confidence matches
            if score > 0.7:
                contexts.append(metadata.get('text', ''))
                sources.append({
                    'filename': metadata.get('filename', 'Unknown'),
                    'page': metadata.get('page', 'N/A'),
                    'score': round(score, 3),
                    'text_preview': metadata.get('text', '')[:200] + '...'
                })
        
        context_text = "\n\n---\n\n".join(contexts)
        return context_text, sources
    
    def _generate_cache_key(self, query: str) -> str:
        """Generate cache key from query"""
        query_hash = hashlib.md5(query.encode()).hexdigest()
        return f"rag:query:{query_hash}"
    
    def _get_from_cache(self, cache_key: str):
        """Get response from Redis cache"""
        try:
            cached = self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache retrieval error: {str(e)}")
        return None
    
    def _save_to_cache(self, cache_key: str, result):
        """Save response to Redis cache"""
        try:
            self.redis.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(result)
            )
        except Exception as e:
            logger.warning(f"Cache save error: {str(e)}")

rag_service = RAGService()
