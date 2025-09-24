"""
Document upload interface for the Streamlit RAG chatbot platform.
Handles PDF file upload, validation, and processing.
"""

import streamlit as st
import logging
from typing import Optional, List
import asyncio

from core.document_processor import DocumentProcessor
from core.vector_store import VectorStoreManager
from utils.config import AppConfig, get_config
from langchain.schema import Document

logger = logging.getLogger(__name__)


def render_document_upload(
    vector_store_manager: VectorStoreManager,
    config: Optional[AppConfig] = None
) -> None:
    """
    Render the document upload interface.
    
    Args:
        vector_store_manager: Vector store manager for creating knowledge bases
        config: Application configuration
    """
    if config is None:
        config = get_config()
    
    st.header("📄 Upload Documents")
    st.write("Upload PDF documents to create or add to a knowledge base.")
    
    # Knowledge base selection/creation
    st.subheader("Knowledge Base")
    
    # Get existing knowledge bases
    existing_kbs = vector_store_manager.list_knowledge_bases()
    kb_names = [kb['name'] for kb in existing_kbs]
    
    # Option to create new or use existing
    kb_option = st.radio(
        "Choose an option:",
        ["Create new knowledge base", "Add to existing knowledge base"],
        key="kb_option"
    )
    
    knowledge_base_name = None
    
    if kb_option == "Create new knowledge base":
        knowledge_base_name = st.text_input(
            "Knowledge Base Name:",
            placeholder="Enter a name for your knowledge base",
            help="This will be used to organize and access your documents",
            key="new_kb_name"
        )
    else:
        if kb_names:
            knowledge_base_name = st.selectbox(
                "Select existing knowledge base:",
                kb_names,
                key="existing_kb_select"
            )
        else:
            st.warning("No existing knowledge bases found. Please create a new one.")
            knowledge_base_name = st.text_input(
                "Knowledge Base Name:",
                placeholder="Enter a name for your knowledge base",
                key="fallback_kb_name"
            )
    
    # File upload
    st.subheader("Document Upload")
    
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type="pdf",
        accept_multiple_files=True,
        help=f"Maximum file size: {config.max_file_size_mb}MB per file",
        key="pdf_uploader"
    )
    
    # Display file information
    if uploaded_files:
        st.write(f"Selected {len(uploaded_files)} file(s):")
        total_size_mb = 0
        
        for file in uploaded_files:
            file_size_mb = len(file.getvalue()) / (1024 * 1024)
            total_size_mb += file_size_mb
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📄 {file.name}")
            with col2:
                st.write(f"{file_size_mb:.1f} MB")
        
        st.write(f"**Total size:** {total_size_mb:.1f} MB")
        
        # Validation
        oversized_files = [
            file for file in uploaded_files 
            if len(file.getvalue()) / (1024 * 1024) > config.max_file_size_mb
        ]
        
        if oversized_files:
            st.error(f"The following files exceed the {config.max_file_size_mb}MB limit:")
            for file in oversized_files:
                file_size_mb = len(file.getvalue()) / (1024 * 1024)
                st.error(f"• {file.name} ({file_size_mb:.1f} MB)")
    
    # Process button
    can_process = (
        knowledge_base_name and 
        knowledge_base_name.strip() and 
        uploaded_files and 
        not any(len(f.getvalue()) / (1024 * 1024) > config.max_file_size_mb for f in uploaded_files)
    )
    
    if st.button(
        "🚀 Process Documents", 
        disabled=not can_process,
        help="Upload and process documents into the knowledge base",
        key="process_button"
    ):
        if can_process:
            asyncio.run(_process_documents(
                uploaded_files, 
                knowledge_base_name.strip(), 
                vector_store_manager,
                kb_option == "Create new knowledge base",
                config
            ))
        else:
            if not knowledge_base_name or not knowledge_base_name.strip():
                st.error("Please enter a knowledge base name.")
            elif not uploaded_files:
                st.error("Please select at least one PDF file.")
    
    # Display existing knowledge bases
    if existing_kbs:
        st.subheader("📚 Existing Knowledge Bases")
        
        for kb in existing_kbs:
            with st.expander(f"📖 {kb['name']} ({kb['document_count']} documents)"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Collection:** {kb['collection_name']}")
                    st.write(f"**Documents:** {kb['document_count']}")
                    # Convert timestamp to readable date
                    import datetime
                    created_date = datetime.datetime.fromtimestamp(kb['created_at'])
                    st.write(f"**Created:** {created_date.strftime('%Y-%m-%d %H:%M')}")
                
                with col2:
                    if st.button(
                        "🗑️ Delete", 
                        key=f"delete_{kb['name']}",
                        help=f"Delete the '{kb['name']}' knowledge base"
                    ):
                        _delete_knowledge_base(kb['name'], vector_store_manager)
    else:
        st.info("No knowledge bases created yet. Upload some documents to get started!")


async def _process_documents(
    uploaded_files: List,
    knowledge_base_name: str,
    vector_store_manager: VectorStoreManager,
    create_new: bool,
    config: AppConfig
) -> None:
    """
    Process uploaded documents and add them to a knowledge base.
    
    Args:
        uploaded_files: List of uploaded files from Streamlit
        knowledge_base_name: Name of the knowledge base
        vector_store_manager: Vector store manager
        create_new: Whether to create a new knowledge base
        config: Application configuration
    """
    try:
        # Initialize document processor
        doc_processor = DocumentProcessor(config)
        
        # Create progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        all_documents = []
        processed_files = 0
        
        for i, uploaded_file in enumerate(uploaded_files):
            try:
                # Update progress
                progress = (i + 0.5) / len(uploaded_files)
                progress_bar.progress(progress)
                status_text.text(f"Processing {uploaded_file.name}...")
                
                # Process the file
                documents = await doc_processor.process_uploaded_file(uploaded_file)
                all_documents.extend(documents)
                processed_files += 1
                
                # Update progress after processing
                progress = (i + 1) / len(uploaded_files)
                progress_bar.progress(progress)
                status_text.text(f"Processed {uploaded_file.name} ({len(documents)} chunks)")
                
                logger.info(f"Successfully processed {uploaded_file.name}: {len(documents)} chunks")
                
            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                logger.error(f"Error processing {uploaded_file.name}: {str(e)}")
                continue
        
        if not all_documents:
            st.error("No documents could be processed. Please check your files and try again.")
            return
        
        # Create or update knowledge base
        status_text.text("Creating/updating knowledge base...")
        
        try:
            if create_new or not vector_store_manager.knowledge_base_exists(knowledge_base_name):
                # Create new knowledge base
                vector_store = vector_store_manager.create_knowledge_base(
                    knowledge_base_name, 
                    all_documents
                )
                st.success(f"✅ Created knowledge base '{knowledge_base_name}' with {len(all_documents)} document chunks from {processed_files} files!")
            else:
                # Add to existing knowledge base
                success = vector_store_manager.add_documents_to_knowledge_base(
                    knowledge_base_name, 
                    all_documents
                )
                if success:
                    st.success(f"✅ Added {len(all_documents)} document chunks from {processed_files} files to existing knowledge base '{knowledge_base_name}'!")
                else:
                    st.error(f"Failed to add documents to knowledge base '{knowledge_base_name}'")
                    return
            
            # Display processing statistics
            doc_stats = doc_processor.get_document_stats(all_documents)
            
            with st.expander("📊 Processing Details"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Files Processed", processed_files)
                with col2:
                    st.metric("Document Chunks", doc_stats['total_chunks'])
                with col3:
                    st.metric("Total Characters", f"{doc_stats['total_chars']:,}")
                
                st.write(f"**Average chunk size:** {doc_stats['average_chunk_size']} characters")
                st.write(f"**Configured chunk size:** {doc_stats['chunk_size_config']} characters")
                st.write(f"**Chunk overlap:** {doc_stats['chunk_overlap_config']} characters")
            
            # Update session state to trigger knowledge base list refresh
            if 'kb_refresh_trigger' not in st.session_state:
                st.session_state.kb_refresh_trigger = 0
            st.session_state.kb_refresh_trigger += 1
            
        except ValueError as ve:
            st.error(f"Error with knowledge base: {str(ve)}")
        except Exception as e:
            st.error(f"Error creating/updating knowledge base: {str(e)}")
            logger.error(f"Error creating/updating knowledge base: {str(e)}")
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
    except Exception as e:
        st.error(f"Unexpected error during document processing: {str(e)}")
        logger.error(f"Unexpected error during document processing: {str(e)}")


def _delete_knowledge_base(name: str, vector_store_manager: VectorStoreManager) -> None:
    """
    Delete a knowledge base after user confirmation.
    
    Args:
        name: Name of the knowledge base to delete
        vector_store_manager: Vector store manager
    """
    try:
        # Confirm deletion
        if st.session_state.get(f'confirm_delete_{name}', False):
            success = vector_store_manager.delete_knowledge_base(name)
            if success:
                st.success(f"✅ Successfully deleted knowledge base '{name}'")
                # Update session state to trigger refresh
                if 'kb_refresh_trigger' not in st.session_state:
                    st.session_state.kb_refresh_trigger = 0
                st.session_state.kb_refresh_trigger += 1
                
                # Clear the confirmation flag
                st.session_state[f'confirm_delete_{name}'] = False
            else:
                st.error(f"Failed to delete knowledge base '{name}'")
        else:
            # Set confirmation flag and rerun
            st.session_state[f'confirm_delete_{name}'] = True
            st.warning(f"Click 'Delete' again to confirm deletion of '{name}'")
            st.rerun()
            
    except Exception as e:
        st.error(f"Error deleting knowledge base '{name}': {str(e)}")
        logger.error(f"Error deleting knowledge base '{name}': {str(e)}")


def get_available_knowledge_bases(vector_store_manager: VectorStoreManager) -> List[str]:
    """
    Get list of available knowledge base names.
    
    Args:
        vector_store_manager: Vector store manager
        
    Returns:
        List of knowledge base names
    """
    try:
        knowledge_bases = vector_store_manager.list_knowledge_bases()
        return [kb['name'] for kb in knowledge_bases]
    except Exception as e:
        logger.error(f"Error getting available knowledge bases: {str(e)}")
        return []