"""
Document processing module for PDF parsing and text chunking.
Handles PDF loading, text extraction, and chunking for RAG pipeline.
"""

import os
import logging
import tempfile
from typing import List, Optional
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from utils.config import AppConfig

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles PDF document processing and text chunking for RAG pipeline."""
    
    def __init__(self, config: Optional[AppConfig] = None):
        """Initialize document processor with configuration."""
        if config is None:
            from utils.config import get_config
            config = get_config()
        
        self.config = config
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            length_function=len,
            add_start_index=True
        )
        
        logger.info(f"Initialized DocumentProcessor with chunk_size={config.chunk_size}, "
                   f"chunk_overlap={config.chunk_overlap}")
    
    async def process_pdf(self, file_path: str) -> List[Document]:
        """
        Process a PDF file and return chunked documents.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of Document objects containing chunked text
            
        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            ValueError: If the file is not a valid PDF
            Exception: For other PDF processing errors
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        if not file_path.lower().endswith('.pdf'):
            raise ValueError(f"File must be a PDF: {file_path}")
        
        try:
            logger.info(f"Processing PDF: {file_path}")
            
            # Load PDF using PyPDFLoader
            loader = PyPDFLoader(file_path)
            documents = await self._load_documents_async(loader)
            
            if not documents:
                raise ValueError(f"No content could be extracted from PDF: {file_path}")
            
            # Split documents into chunks
            chunked_documents = self.text_splitter.split_documents(documents)
            
            logger.info(f"Successfully processed PDF: {file_path}, "
                       f"extracted {len(documents)} pages, "
                       f"created {len(chunked_documents)} chunks")
            
            return chunked_documents
            
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {str(e)}")
            raise
    
    async def _load_documents_async(self, loader: PyPDFLoader) -> List[Document]:
        """Load documents asynchronously if supported, otherwise use sync method."""
        try:
            # Try async loading first
            return await loader.aload()
        except AttributeError:
            # Fallback to synchronous loading
            return loader.load()
    
    async def process_uploaded_file(self, uploaded_file) -> List[Document]:
        """
        Process an uploaded file (from Streamlit file uploader) and return chunked documents.
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            List of Document objects containing chunked text
        """
        # Validate file type
        if not uploaded_file.name.lower().endswith('.pdf'):
            raise ValueError("Only PDF files are supported")
        
        # Validate file size
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        if file_size_mb > self.config.max_file_size_mb:
            raise ValueError(f"File too large: {file_size_mb:.1f}MB. "
                           f"Maximum allowed: {self.config.max_file_size_mb}MB")
        
        # Create temporary file
        temp_dir = Path(self.config.upload_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        temp_file_path = None
        try:
            # Save uploaded file to temporary location
            temp_file_path = temp_dir / f"temp_{uploaded_file.name}"
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(uploaded_file.getvalue())
            
            # Process the temporary file
            documents = await self.process_pdf(str(temp_file_path))
            
            # Add metadata about the original file
            import datetime
            for doc in documents:
                doc.metadata.update({
                    'original_filename': uploaded_file.name,
                    'file_size_mb': file_size_mb,
                    'processed_at': datetime.datetime.now().isoformat()
                })
            
            return documents
            
        except Exception as e:
            logger.error(f"Error processing uploaded file {uploaded_file.name}: {str(e)}")
            raise
        finally:
            # Clean up temporary file
            if temp_file_path and temp_file_path.exists():
                try:
                    temp_file_path.unlink()
                    logger.debug(f"Cleaned up temporary file: {temp_file_path}")
                except Exception as cleanup_error:
                    logger.warning(f"Failed to clean up temporary file {temp_file_path}: {cleanup_error}")
    
    def get_document_stats(self, documents: List[Document]) -> dict:
        """
        Get statistics about processed documents.
        
        Args:
            documents: List of processed Document objects
            
        Returns:
            Dictionary containing document statistics
        """
        if not documents:
            return {"total_chunks": 0, "total_chars": 0, "average_chunk_size": 0}
        
        total_chars = sum(len(doc.page_content) for doc in documents)
        
        return {
            "total_chunks": len(documents),
            "total_chars": total_chars,
            "average_chunk_size": total_chars // len(documents) if documents else 0,
            "chunk_size_config": self.config.chunk_size,
            "chunk_overlap_config": self.config.chunk_overlap
        }