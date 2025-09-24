"""
Unit tests for the document processor module.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add src to path for testing
import sys
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from core.document_processor import DocumentProcessor
from utils.config import AppConfig
from langchain.schema import Document


class TestDocumentProcessor:
    """Test cases for DocumentProcessor class."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return AppConfig(
            openai_api_key="test-key",
            chunk_size=100,
            chunk_overlap=20,
            upload_dir="test_uploads",
            max_file_size_mb=10
        )
    
    @pytest.fixture
    def processor(self, config):
        """Create DocumentProcessor instance."""
        return DocumentProcessor(config)
    
    def test_initialization(self, processor, config):
        """Test processor initialization."""
        assert processor.config == config
        assert processor.text_splitter.chunk_size == config.chunk_size
        assert processor.text_splitter.chunk_overlap == config.chunk_overlap
    
    @pytest.mark.asyncio
    async def test_process_pdf_file_not_found(self, processor):
        """Test processing non-existent PDF file."""
        with pytest.raises(FileNotFoundError):
            await processor.process_pdf("nonexistent.pdf")
    
    @pytest.mark.asyncio
    async def test_process_pdf_invalid_extension(self, processor):
        """Test processing file with invalid extension."""
        with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
            with pytest.raises(ValueError, match="File must be a PDF"):
                await processor.process_pdf(temp_file.name)
    
    @pytest.mark.asyncio
    @patch('core.document_processor.PyPDFLoader')
    async def test_process_pdf_success(self, mock_loader_class, processor):
        """Test successful PDF processing."""
        # Mock the PyPDFLoader
        mock_loader = Mock()
        mock_loader.aload = AsyncMock(return_value=[
            Document(page_content="Test content page 1", metadata={"page": 1}),
            Document(page_content="Test content page 2", metadata={"page": 2})
        ])
        mock_loader_class.return_value = mock_loader
        
        # Create a temporary PDF file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(b"fake pdf content")
            temp_path = temp_file.name
        
        try:
            result = await processor.process_pdf(temp_path)
            
            # Verify results
            assert isinstance(result, list)
            assert len(result) > 0  # Should have chunks from text splitting
            assert all(isinstance(doc, Document) for doc in result)
            
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_process_uploaded_file_invalid_type(self, processor):
        """Test processing uploaded file with invalid type."""
        mock_file = Mock()
        mock_file.name = "test.txt"
        
        with pytest.raises(ValueError, match="Only PDF files are supported"):
            await processor.process_uploaded_file(mock_file)
    
    @pytest.mark.asyncio
    async def test_process_uploaded_file_too_large(self, processor):
        """Test processing uploaded file that's too large."""
        mock_file = Mock()
        mock_file.name = "test.pdf"
        mock_file.getvalue.return_value = b"x" * (15 * 1024 * 1024)  # 15MB
        
        with pytest.raises(ValueError, match="File too large"):
            await processor.process_uploaded_file(mock_file)
    
    def test_get_document_stats_empty(self, processor):
        """Test getting stats for empty document list."""
        stats = processor.get_document_stats([])
        
        assert stats["total_chunks"] == 0
        assert stats["total_chars"] == 0
        assert stats["average_chunk_size"] == 0
    
    def test_get_document_stats_with_documents(self, processor):
        """Test getting stats for document list."""
        documents = [
            Document(page_content="Short content"),
            Document(page_content="This is longer content for testing")
        ]
        
        stats = processor.get_document_stats(documents)
        
        assert stats["total_chunks"] == 2
        assert stats["total_chars"] == len("Short content") + len("This is longer content for testing")
        assert stats["average_chunk_size"] > 0
        assert stats["chunk_size_config"] == processor.config.chunk_size