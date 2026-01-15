from pinecone import Pinecone, ServerlessSpec
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger()

class PineconeService:
    def __init__(self):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME
        self.index = None
        
    def initialize_index(self, dimension: int = 1536):
        """Initialize Pinecone index if it doesn't exist"""
        try:
            # Check if index exists
            existing_indexes = self.pc.list_indexes()
            index_names = [idx['name'] for idx in existing_indexes]
            
            if self.index_name not in index_names:
                logger.info(f"Creating new Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                logger.info(f"Index {self.index_name} created successfully")
            else:
                logger.info(f"Index {self.index_name} already exists")
            
            self.index = self.pc.Index(self.index_name)
            return self.index
            
        except Exception as e:
            logger.error(f"Error initializing Pinecone index: {str(e)}")
            raise
    
    def get_index(self):
        """Get Pinecone index"""
        if self.index is None:
            self.index = self.pc.Index(self.index_name)
        return self.index
    
    def upsert_vectors(self, vectors: list):
        """Upsert vectors to Pinecone"""
        try:
            index = self.get_index()
            index.upsert(vectors=vectors)
            logger.info(f"Upserted {len(vectors)} vectors to Pinecone")
        except Exception as e:
            logger.error(f"Error upserting vectors: {str(e)}")
            raise
    
    def query_vectors(self, query_vector: list, top_k: int = 5, filter_dict: dict = None):
        """Query vectors from Pinecone"""
        try:
            index = self.get_index()
            results = index.query(
                vector=query_vector,
                top_k=top_k,
                filter=filter_dict,
                include_metadata=True
            )
            return results
        except Exception as e:
            logger.error(f"Error querying vectors: {str(e)}")
            raise

pinecone_service = PineconeService()
