from app.services.embedding_service import embedding_service
from app.services.pinecone_service import pinecone_service
from app.services.llm_service import llm_service
from app.core.redis_client import get_redis
from app.core.logger import get_logger
from app.core.exceptions import RAGException, LLMException, CacheException, handle_service_error
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
    
    def _is_greeting(self, message: str) -> bool:
        """Detect if message is a greeting"""
        greetings = [
            'hola', 'buenos días', 'buenas tardes', 'buenas noches',
            'qué tal', 'saludos', 'hey', 'hi', 'hello', 'buen día'
        ]
        msg_lower = message.lower().strip()
        return any(greeting in msg_lower for greeting in greetings)
    
    def _is_portal_question(self, message: str) -> bool:
        """Detect if message is about portals"""
        portal_keywords = [
            'portal', 'portales', 'intermediario', 'intermediarios',
            'portal de ideas', 'portal idea', 'plataforma',
            'donde cotizar', 'dónde cotizar', 'donde cotizo'
        ]
        msg_lower = message.lower().strip()
        return any(keyword in msg_lower for keyword in portal_keywords)
    
    def _needs_comprehensive_search(self, message: str) -> bool:
        """Detect if message needs comprehensive information (all details)"""
        msg_lower = message.lower().strip()
        
        # Palabras que indican que se pregunta sobre características específicas
        specific_feature_keywords = [
            # Periodos y tiempos
            'periodos de espera', 'periodo de espera', 'períodos de espera', 'período de espera',
            'tiempo de espera', 'tiempos de espera', 'cuánto tiempo',
            # Costos y pagos
            'deducible', 'deducibles', 'coaseguro', 'coaseguros', 'copago', 'copagos',
            'precio', 'precios', 'costo', 'costos', 'prima', 'primas', 'tarifa', 'tarifas',
            # Coberturas y beneficios
            'cobertura', 'coberturas', 'beneficio', 'beneficios', 'servicio', 'servicios',
            'incluye', 'cubre', 'protege', 'ampara',
            # Exclusiones y limitaciones
            'exclusiones', 'exclusión', 'limitaciones', 'limitación', 'restricciones', 'restricción',
            'no cubre', 'no incluye', 'excepto', 'salvo',
            # Requisitos y documentación
            'requisitos', 'requisito', 'documentos', 'documento', 'papeles', 'trámites', 'trámite',
            # Listas completas
            'lista completa', 'todos los', 'todas las', 'todo lo que', 'cuáles son todos',
            'lista de', 'listado de', 'relación de',
            # Condiciones
            'condiciones', 'condición', 'cláusula', 'cláusulas', 'términos',
            # Sumas aseguradas y límites
            'suma asegurada', 'sumas aseguradas', 'límite', 'límites', 'tope', 'topes',
            'monto', 'montos', 'máximo', 'máximos', 'mínimo', 'mínimos'
        ]
        
        # Detectar si menciona un producto específico + alguna característica
        productos = [
            'versátil', 'versatil', 'premium', 'platino', 'conexión gnp',
            'gmm', 'gastos médicos', 'vida', 'auto', 'autos', 'daños',
            'hogar', 'mascota', 'negocio protegido', 'cyber safe'
        ]
        
        has_product = any(prod in msg_lower for prod in productos)
        has_feature = any(keyword in msg_lower for keyword in specific_feature_keywords)
        
        # Si pregunta sobre un producto Y una característica específica, necesita búsqueda comprehensiva
        return has_product and has_feature
    
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
            # Validate input
            if not user_query or not user_query.strip():
                raise RAGException(
                    message="La consulta no puede estar vacía",
                    details={"type": "validation_error"}
                )
            
            # Detectar saludos y responder directamente
            if self._is_greeting(user_query):
                logger.info("Greeting detected, responding directly")
                try:
                    response, tokens_used = self.llm_service.generate_response(
                        user_message=user_query,
                        context="",  # Sin contexto para saludos
                        conversation_history=conversation_history
                    )
                    return (response, [], tokens_used)
                except Exception as e:
                    logger.error(f"LLM error on greeting: {str(e)}")
                    raise handle_service_error("GPT-4o API", e)
            
            # Detectar preguntas sobre portales y responder con contexto del system prompt
            if self._is_portal_question(user_query):
                logger.info("Portal question detected, using system prompt context")
                try:
                    # El system prompt ya tiene información sobre portales
                    response, tokens_used = self.llm_service.generate_response(
                        user_message=user_query,
                        context="",  # El contexto de portales está en el system prompt
                        conversation_history=conversation_history
                    )
                    return (response, [], tokens_used)
                except Exception as e:
                    logger.error(f"LLM error on portal question: {str(e)}")
                    raise handle_service_error("GPT-4o API", e)
            
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
            
            # Búsqueda con manejo de errores
            all_chunks = []
            seen_ids = set()
            
            # Detectar si necesita búsqueda comprehensiva (más chunks)
            chunks_per_query = 30 if self._needs_comprehensive_search(user_query) else 15
            max_final_chunks = 35 if self._needs_comprehensive_search(user_query) else 20
            
            if self._needs_comprehensive_search(user_query):
                logger.info("Comprehensive search detected - using more chunks")
            
            try:
                for sq in search_queries:
                    # Generate embedding
                    try:
                        query_embedding = self.embedding_service.generate_embedding(sq)
                    except Exception as e:
                        logger.error(f"Embedding error: {str(e)}")
                        raise handle_service_error("OpenAI Embeddings", e)
                    
                    # Query Pinecone
                    try:
                        results = self.pinecone_service.query_vectors(
                            query_vector=query_embedding,
                            top_k=chunks_per_query  # Dinámico según tipo de pregunta
                        )
                    except Exception as e:
                        logger.error(f"Pinecone query error: {str(e)}")
                        raise handle_service_error("Pinecone", e)
                    
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
            
            except RAGException:
                raise  # Re-raise our custom exceptions
            except Exception as e:
                logger.error(f"Search error: {str(e)}")
                raise RAGException(
                    message="Error al buscar en la base de conocimiento",
                    details={"error": str(e)}
                )
            
            # Priorizar documentos sintéticos (tienen info consolidada)
            all_chunks.sort(key=lambda x: (
                1 if 'synthetic' in x['doc_type'] else 0,  # Sintéticos primero
                x['score']  # Luego por score
            ), reverse=True)
            
            # Tomar top chunks (dinámico según tipo de pregunta)
            top_chunks = all_chunks[:max_final_chunks]
            
            if not top_chunks:
                logger.warning("No relevant chunks found")
                return (
                    "Lo siento, no encontré información relevante sobre esa pregunta en los manuales de GNP. "
                    "¿Podrías reformular tu pregunta o ser más específico?",
                    [],
                    0
                )
            
            # Construir contexto
            context_text = "\n\n---\n\n".join([c['text'] for c in top_chunks])
            
            logger.info(f"Found {len(top_chunks)} chunks (best: {top_chunks[0]['score']:.3f})")
            logger.info(f"Context size: {len(context_text)} chars")
            
            # Generar respuesta con manejo de errores
            try:
                response, tokens_used = self.llm_service.generate_response(
                    user_message=user_query,
                    context=context_text,
                    conversation_history=conversation_history
                )
            except Exception as e:
                logger.error(f"LLM error: {str(e)}")
                raise handle_service_error("Claude API", e)
            
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
            
        except (RAGException, LLMException):
            # Re-raise custom exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error in RAG query: {str(e)}")
            raise RAGException(
                message="Ocurrió un error al procesar tu consulta",
                details={"error": str(e)}
            )
    
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
        return f"rag:v3:{query_hash}"  # v3 para nueva versión con portales
    
    def _get_from_cache(self, cache_key: str):
        """Get from cache with error handling"""
        try:
            cached = self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        except json.JSONDecodeError as e:
            logger.warning(f"Cache JSON decode error: {str(e)}")
            # Delete corrupted cache entry
            try:
                self.redis.delete(cache_key)
            except:
                pass
        except Exception as e:
            logger.warning(f"Cache get error: {str(e)}")
            # Cache errors should not break the app
        return None
    
    def _save_to_cache(self, cache_key: str, result):
        """Save to cache with error handling"""
        try:
            self.redis.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(result)
            )
        except Exception as e:
            logger.warning(f"Cache save error: {str(e)}")
            # Cache errors should not break the app

rag_service = RAGService()
