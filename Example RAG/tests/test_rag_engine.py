"""
Unit tests for the RAG engine module.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

# Add src to path for testing
import sys
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from core.rag_engine import RAGEngine
from core.conversation_manager import ConversationManager
from utils.config import AppConfig
from langchain.schema import Document


class TestRAGEngine:
    """Test cases for RAGEngine class."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return AppConfig(
            openai_api_key="test-key",
            openai_model="gpt-4",
            max_conversation_history=3
        )
    
    @pytest.fixture
    def mock_vector_store(self):
        """Create mock vector store."""
        mock_store = Mock()
        mock_retriever = Mock()
        mock_store.as_retriever.return_value = mock_retriever
        return mock_store
    
    @pytest.fixture
    def mock_conversation_manager(self):
        """Create mock conversation manager."""
        return Mock(spec=ConversationManager)
    
    @pytest.fixture
    @patch('core.rag_engine.ChatOpenAI')
    @patch('core.rag_engine.ConversationalRetrievalChain')
    def rag_engine(self, mock_chain, mock_llm, mock_vector_store, mock_conversation_manager, config):
        """Create RAGEngine instance with mocked dependencies."""
        return RAGEngine(mock_vector_store, mock_conversation_manager, config)
    
    def test_initialization(self, rag_engine, config, mock_vector_store, mock_conversation_manager):
        """Test RAG engine initialization."""
        assert rag_engine.config == config
        assert rag_engine.vector_store == mock_vector_store
        assert rag_engine.conversation_manager == mock_conversation_manager
        assert rag_engine.retriever is not None
    
    @pytest.mark.asyncio
    async def test_retrieve_documents(self, rag_engine):
        """Test document retrieval."""
        # Mock retriever
        mock_docs = [
            Document(page_content="Test content 1"),
            Document(page_content="Test content 2")
        ]
        rag_engine.retriever.aget_relevant_documents = AsyncMock(return_value=mock_docs)
        
        result = await rag_engine._retrieve_documents("test question")
        
        assert result == mock_docs
        rag_engine.retriever.aget_relevant_documents.assert_called_once_with("test question")
    
    @pytest.mark.asyncio
    async def test_retrieve_documents_fallback_sync(self, rag_engine):
        """Test document retrieval fallback to sync method."""
        # Mock retriever without async method
        mock_docs = [Document(page_content="Test content")]
        rag_engine.retriever.get_relevant_documents = Mock(return_value=mock_docs)
        # Remove async method to trigger fallback
        if hasattr(rag_engine.retriever, 'aget_relevant_documents'):
            delattr(rag_engine.retriever, 'aget_relevant_documents')
        
        result = await rag_engine._retrieve_documents("test question")
        
        assert result == mock_docs
    
    def test_prepare_context_empty(self, rag_engine):
        """Test context preparation with empty documents."""
        result = rag_engine._prepare_context([])
        
        assert "No relevant context found" in result
    
    def test_prepare_context_with_documents(self, rag_engine):
        """Test context preparation with documents."""
        documents = [
            Document(page_content="Content 1", metadata={"source": "doc1.pdf", "page": 1}),
            Document(page_content="Content 2", metadata={"source": "doc2.pdf", "page": 2})
        ]
        
        result = rag_engine._prepare_context(documents)
        
        assert "Content 1" in result
        assert "Content 2" in result
        assert "doc1.pdf" in result
        assert "doc2.pdf" in result
        assert "Page 1" in result
        assert "Page 2" in result
    
    def test_get_source_documents(self, rag_engine):
        """Test getting source documents synchronously."""
        mock_docs = [Document(page_content="Test content")]
        rag_engine.retriever.get_relevant_documents = Mock(return_value=mock_docs)
        
        result = rag_engine.get_source_documents("test question")
        
        assert result == mock_docs
        rag_engine.retriever.get_relevant_documents.assert_called_once_with("test question")
    
    def test_get_source_documents_error(self, rag_engine):
        """Test getting source documents with error."""
        rag_engine.retriever.get_relevant_documents = Mock(side_effect=Exception("Test error"))
        
        result = rag_engine.get_source_documents("test question")
        
        assert result == []
    
    def test_update_vector_store(self, rag_engine, mock_conversation_manager, config):
        """Test updating vector store."""
        new_mock_store = Mock()
        new_mock_retriever = Mock()
        new_mock_store.as_retriever.return_value = new_mock_retriever
        
        with patch('core.rag_engine.ConversationalRetrievalChain'):
            rag_engine.update_vector_store(new_mock_store)
        
        assert rag_engine.vector_store == new_mock_store
        assert rag_engine.retriever == new_mock_retriever
    
    def test_get_engine_stats(self, rag_engine, mock_conversation_manager, config):
        """Test getting engine statistics."""
        # Mock collection
        mock_collection = Mock()
        mock_collection.count.return_value = 25
        rag_engine.vector_store._collection = mock_collection
        
        # Mock conversation stats
        mock_conversation_manager.get_conversation_summary.return_value = {
            "conversation_active": True,
            "total_session_messages": 4
        }
        
        result = rag_engine.get_engine_stats()
        
        assert result["model"] == config.openai_model
        assert result["vector_store_documents"] == 25
        assert result["conversation_active"] == True
        assert result["total_messages"] == 4
        assert result["memory_limit"] == config.max_conversation_history
    
    def test_get_engine_stats_error(self, rag_engine):
        """Test getting engine statistics with error."""
        rag_engine.vector_store._collection = Mock(side_effect=Exception("Test error"))
        
        result = rag_engine.get_engine_stats()
        
        assert "error" in result