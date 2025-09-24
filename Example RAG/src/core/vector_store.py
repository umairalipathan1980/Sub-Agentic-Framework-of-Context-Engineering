"""
Vector store management using Chroma database.
Handles knowledge base creation, document storage, and semantic search.
"""

import os
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

from utils.config import AppConfig

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Manages Chroma vector database operations for knowledge bases."""
    
    def __init__(self, config: Optional[AppConfig] = None):
        """Initialize vector store manager with configuration."""
        if config is None:
            from utils.config import get_config
            config = get_config()
        
        self.config = config
        self.persist_directory = Path(config.chroma_persist_dir)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize OpenAI embeddings
        try:
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=config.openai_api_key,
                model="text-embedding-3-small"  # Using smaller model for efficiency
            )
            logger.info("Initialized OpenAI embeddings")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI embeddings: {e}")
            raise
        
        logger.info(f"Initialized VectorStoreManager with persist_directory: {self.persist_directory}")
    
    def create_knowledge_base(self, name: str, documents: List[Document]) -> Chroma:
        """
        Create a new knowledge base with the given documents.
        
        Args:
            name: Name of the knowledge base (used as collection name)
            documents: List of Document objects to store
            
        Returns:
            Chroma vector store instance
            
        Raises:
            ValueError: If knowledge base name is invalid or already exists
            Exception: For other vector store creation errors
        """
        if not name or not name.strip():
            raise ValueError("Knowledge base name cannot be empty")
        
        # Sanitize collection name (Chroma has specific requirements)
        collection_name = self._sanitize_collection_name(name)
        
        if self.knowledge_base_exists(collection_name):
            raise ValueError(f"Knowledge base '{name}' already exists")
        
        if not documents:
            raise ValueError("Cannot create knowledge base with no documents")
        
        try:
            logger.info(f"Creating knowledge base '{name}' with {len(documents)} documents")
            
            vector_store = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=str(self.persist_directory)
            )
            
            # Add documents to the vector store
            vector_store.add_documents(documents)
            
            logger.info(f"Successfully created knowledge base '{name}' with collection '{collection_name}'")
            return vector_store
            
        except Exception as e:
            logger.error(f"Error creating knowledge base '{name}': {str(e)}")
            raise
    
    def get_knowledge_base(self, name: str) -> Optional[Chroma]:
        """
        Load an existing knowledge base.
        
        Args:
            name: Name of the knowledge base
            
        Returns:
            Chroma vector store instance if it exists, None otherwise
        """
        collection_name = self._sanitize_collection_name(name)
        
        if not self.knowledge_base_exists(collection_name):
            logger.warning(f"Knowledge base '{name}' does not exist")
            return None
        
        try:
            vector_store = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=str(self.persist_directory)
            )
            
            logger.info(f"Successfully loaded knowledge base '{name}'")
            return vector_store
            
        except Exception as e:
            logger.error(f"Error loading knowledge base '{name}': {str(e)}")
            return None
    
    def knowledge_base_exists(self, name: str) -> bool:
        """
        Check if a knowledge base exists.
        
        Args:
            name: Name of the knowledge base
            
        Returns:
            True if the knowledge base exists, False otherwise
        """
        collection_name = self._sanitize_collection_name(name)
        
        try:
            # Try to create a temporary Chroma instance to check if collection exists
            temp_chroma = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=str(self.persist_directory)
            )
            
            # Check if the collection has any documents
            # If it doesn't exist, this will create an empty collection
            collection = temp_chroma._collection
            count = collection.count()
            
            # If count is 0, it might be a new collection, so we delete it
            if count == 0:
                try:
                    collection.delete()
                    return False
                except:
                    pass
            
            return count > 0
            
        except Exception as e:
            logger.debug(f"Error checking knowledge base existence for '{name}': {str(e)}")
            return False
    
    def list_knowledge_bases(self) -> List[Dict[str, Any]]:
        """
        List all available knowledge bases.
        
        Returns:
            List of dictionaries containing knowledge base information
        """
        knowledge_bases = []
        
        try:
            # Check for existing Chroma database files
            if not self.persist_directory.exists():
                return knowledge_bases
            
            # Import ChromaDB client to list collections
            import chromadb
            
            # Create a client to access the database
            client = chromadb.PersistentClient(path=str(self.persist_directory))
            
            # List all collections
            collections = client.list_collections()
            
            for collection in collections:
                try:
                    # Get collection info
                    count = collection.count()
                    
                    if count > 0:
                        # Try to get metadata or use collection name
                        collection_name = collection.name
                        
                        # Convert sanitized name back to display name
                        display_name = collection_name.replace('_', ' ').title()
                        
                        knowledge_bases.append({
                            'name': display_name,
                            'collection_name': collection_name,
                            'document_count': count,
                            'created_at': 0  # ChromaDB doesn't provide creation time easily
                        })
                        
                except Exception as e:
                    logger.debug(f"Could not get info for collection {collection.name}: {e}")
                    continue
            
            logger.info(f"Found {len(knowledge_bases)} knowledge bases")
            return sorted(knowledge_bases, key=lambda x: x['name'])
            
        except Exception as e:
            logger.error(f"Error listing knowledge bases: {str(e)}")
            return []
    
    def delete_knowledge_base(self, name: str) -> bool:
        """
        Delete a knowledge base.
        
        Args:
            name: Name of the knowledge base to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        collection_name = self._sanitize_collection_name(name)
        
        try:
            if not self.knowledge_base_exists(collection_name):
                logger.warning(f"Cannot delete knowledge base '{name}' - it doesn't exist")
                return False
            
            # Load the collection and delete it
            chroma = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=str(self.persist_directory)
            )
            
            collection = chroma._collection
            collection.delete()
            
            logger.info(f"Successfully deleted knowledge base '{name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting knowledge base '{name}': {str(e)}")
            return False
    
    def add_documents_to_knowledge_base(self, name: str, documents: List[Document]) -> bool:
        """
        Add documents to an existing knowledge base.
        
        Args:
            name: Name of the knowledge base
            documents: List of Document objects to add
            
        Returns:
            True if documents were added successfully, False otherwise
        """
        vector_store = self.get_knowledge_base(name)
        if not vector_store:
            logger.error(f"Cannot add documents to non-existent knowledge base '{name}'")
            return False
        
        try:
            vector_store.add_documents(documents)
            logger.info(f"Successfully added {len(documents)} documents to knowledge base '{name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to knowledge base '{name}': {str(e)}")
            return False
    
    def _sanitize_collection_name(self, name: str) -> str:
        """
        Sanitize collection name to meet Chroma requirements.
        
        Args:
            name: Original name
            
        Returns:
            Sanitized collection name
        """
        # Chroma collection names must be alphanumeric with underscores and hyphens
        sanitized = "".join(c if c.isalnum() or c in "-_" else "_" for c in name.strip())
        
        # Ensure it starts with a letter or number
        if sanitized and not sanitized[0].isalnum():
            sanitized = "kb_" + sanitized
        
        # Ensure it's not empty
        if not sanitized:
            sanitized = "default_kb"
        
        return sanitized.lower()
    
    def get_knowledge_base_stats(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics about a knowledge base.
        
        Args:
            name: Name of the knowledge base
            
        Returns:
            Dictionary containing statistics, or None if knowledge base doesn't exist
        """
        vector_store = self.get_knowledge_base(name)
        if not vector_store:
            return None
        
        try:
            collection = vector_store._collection
            count = collection.count()
            
            return {
                'name': name,
                'document_count': count,
                'collection_name': self._sanitize_collection_name(name),
                'persist_directory': str(self.persist_directory)
            }
            
        except Exception as e:
            logger.error(f"Error getting stats for knowledge base '{name}': {str(e)}")
            return None