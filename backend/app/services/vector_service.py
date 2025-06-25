"""
Vector Store Service using Qdrant for RAG implementation
"""
from typing import List, Dict, Any, Optional
from uuid import uuid4
import logging

from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from ..core.config import settings

logger = logging.getLogger(__name__)


class VectorService:
    """Service for managing vector embeddings and similarity search"""
    
    def __init__(self):
        self.client = None
        self.embeddings = None
        self.vector_store = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Qdrant client and embeddings"""
        try:
            # Initialize Qdrant client
            self.client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT
            )
            
            # Initialize OpenAI embeddings
            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",
                openai_api_key=settings.OPENAI_API_KEY
            )
            
            # Create collection if it doesn't exist
            collection_name = "ai_tutor_knowledge"
            try:
                self.client.get_collection(collection_name)
            except Exception:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=1536,  # OpenAI embedding dimension
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {collection_name}")
            
            # Initialize vector store
            self.vector_store = QdrantVectorStore(
                client=self.client,
                collection_name=collection_name,
                embedding=self.embeddings
            )
            
            logger.info("Vector service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector service: {e}")
            # Don't raise exception in initialization - allow system to start
            self.client = None
            self.embeddings = None
            self.vector_store = None
    
    async def add_documents(
        self,
        documents: List[Document],
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Add documents to the vector store"""
        try:
            # Generate unique IDs for documents
            ids = [str(uuid4()) for _ in documents]
            
            # Add metadata to documents if provided
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)
            
            # Add documents to vector store
            self.vector_store.add_documents(documents=documents, ids=ids)
            
            logger.info(f"Added {len(documents)} documents to vector store")
            return ids
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    async def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """Perform similarity search on the vector store"""
        try:
            # Perform search
            if filter_dict:
                results = self.vector_store.similarity_search(
                    query=query,
                    k=k,
                    filter=filter_dict
                )
            else:
                results = self.vector_store.similarity_search(
                    query=query,
                    k=k
                )
            
            logger.info(f"Found {len(results)} similar documents for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Failed to perform similarity search: {e}")
            raise
    
    async def delete_documents(self, ids: List[str]) -> bool:
        """Delete documents from the vector store by IDs"""
        try:
            self.vector_store.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents from vector store")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            raise


# Singleton instance
vector_service = VectorService()