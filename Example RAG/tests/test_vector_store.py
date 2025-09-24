"""
Unit tests for the vector store manager module.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path for testing
import sys
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from core.vector_store import VectorStoreManager
from utils.config import AppConfig
from langchain.schema import Document


class TestVectorStoreManager:
    """Test cases for VectorStoreManager class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def config(self, temp_dir):
        """Create test configuration."""
        return AppConfig(
            openai_api_key="test-key",
            chroma_persist_dir=str(temp_dir / "chroma")
        )
    
    @pytest.fixture
    @patch('core.vector_store.OpenAIEmbeddings')
    def vector_store_manager(self, mock_embeddings, config):
        """Create VectorStoreManager instance with mocked embeddings."""
        mock_embeddings.return_value = Mock()
        return VectorStoreManager(config)
    
    def test_initialization(self, vector_store_manager, config):
        """Test vector store manager initialization."""
        assert vector_store_manager.config == config
        assert vector_store_manager.persist_directory.exists()
    
    def test_sanitize_collection_name(self, vector_store_manager):
        """Test collection name sanitization."""
        # Test various inputs
        assert vector_store_manager._sanitize_collection_name("Test KB") == "test_kb"
        assert vector_store_manager._sanitize_collection_name("My-Knowledge_Base") == "my-knowledge_base"
        assert vector_store_manager._sanitize_collection_name("123 Numbers") == "123_numbers"
        assert vector_store_manager._sanitize_collection_name("") == "default_kb"
        assert vector_store_manager._sanitize_collection_name("Special@#$Chars") == "kb_special___chars"
    
    @patch('core.vector_store.Chroma')
    def test_create_knowledge_base_success(self, mock_chroma, vector_store_manager):
        """Test successful knowledge base creation."""
        # Mock Chroma
        mock_vector_store = Mock()
        mock_chroma.return_value = mock_vector_store
        
        # Mock knowledge base existence check
        vector_store_manager.knowledge_base_exists = Mock(return_value=False)
        
        # Test documents
        documents = [
            Document(page_content="Test content 1"),
            Document(page_content="Test content 2")
        ]
        
        result = vector_store_manager.create_knowledge_base("Test KB", documents)
        
        # Verify
        assert result == mock_vector_store
        mock_vector_store.add_documents.assert_called_once_with(documents)
    
    def test_create_knowledge_base_empty_name(self, vector_store_manager):
        """Test knowledge base creation with empty name."""
        documents = [Document(page_content="Test")]
        
        with pytest.raises(ValueError, match="Knowledge base name cannot be empty"):
            vector_store_manager.create_knowledge_base("", documents)
    
    def test_create_knowledge_base_no_documents(self, vector_store_manager):
        """Test knowledge base creation with no documents."""
        with pytest.raises(ValueError, match="Cannot create knowledge base with no documents"):
            vector_store_manager.create_knowledge_base("Test KB", [])
    
    def test_create_knowledge_base_already_exists(self, vector_store_manager):
        """Test knowledge base creation when it already exists."""
        vector_store_manager.knowledge_base_exists = Mock(return_value=True)
        documents = [Document(page_content="Test")]
        
        with pytest.raises(ValueError, match="already exists"):
            vector_store_manager.create_knowledge_base("Existing KB", documents)
    
    @patch('core.vector_store.Chroma')
    def test_get_knowledge_base_success(self, mock_chroma, vector_store_manager):
        """Test successful knowledge base retrieval."""
        mock_vector_store = Mock()
        mock_chroma.return_value = mock_vector_store
        vector_store_manager.knowledge_base_exists = Mock(return_value=True)
        
        result = vector_store_manager.get_knowledge_base("Test KB")
        
        assert result == mock_vector_store
    
    def test_get_knowledge_base_not_exists(self, vector_store_manager):
        """Test knowledge base retrieval when it doesn't exist."""
        vector_store_manager.knowledge_base_exists = Mock(return_value=False)
        
        result = vector_store_manager.get_knowledge_base("Nonexistent KB")
        
        assert result is None
    
    def test_list_knowledge_bases_empty(self, vector_store_manager):
        """Test listing knowledge bases when none exist."""
        result = vector_store_manager.list_knowledge_bases()
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    @patch('core.vector_store.Chroma')
    def test_get_knowledge_base_stats(self, mock_chroma, vector_store_manager):
        """Test getting knowledge base statistics."""
        # Mock vector store
        mock_vector_store = Mock()
        mock_collection = Mock()
        mock_collection.count.return_value = 42
        mock_vector_store._collection = mock_collection
        
        vector_store_manager.get_knowledge_base = Mock(return_value=mock_vector_store)
        
        result = vector_store_manager.get_knowledge_base_stats("Test KB")
        
        assert result is not None
        assert result["name"] == "Test KB"
        assert result["document_count"] == 42
        assert "collection_name" in result
        assert "persist_directory" in result
    
    def test_get_knowledge_base_stats_not_exists(self, vector_store_manager):
        """Test getting stats for non-existent knowledge base."""
        vector_store_manager.get_knowledge_base = Mock(return_value=None)
        
        result = vector_store_manager.get_knowledge_base_stats("Nonexistent KB")
        
        assert result is None