"""
Main Streamlit application for the RAG Chatbot Platform.
Provides the primary interface for knowledge base management and chat functionality.
"""

import streamlit as st
import logging
from typing import Optional
import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from utils.config import get_config, ensure_directories_exist
from core.vector_store import VectorStoreManager
from core.conversation_manager import ConversationManager
from core.rag_engine import RAGEngine
from application.document_upload import render_document_upload, get_available_knowledge_bases
from application.chat_interface import render_chat_interface, render_chat_controls

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Main application entry point."""
    try:
        # Configure Streamlit page
        st.set_page_config(
            page_title="RAG Chatbot Platform",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                'Get Help': None,
                'Report a bug': None,
                'About': "RAG Chatbot Platform - Chat with your documents using AI"
            }
        )
        
        # Load configuration
        config = get_config()
        
        # Ensure required directories exist
        ensure_directories_exist(config)
        
        # Initialize session state
        _initialize_session_state()
        
        # Check for OpenAI API key
        if not config.openai_api_key:
            _render_api_key_setup()
            return
        
        # Initialize managers
        vector_store_manager = _get_vector_store_manager(config)
        conversation_manager = _get_conversation_manager(config)
        
        # Render sidebar
        _render_sidebar(vector_store_manager, conversation_manager)
        
        # Get selected knowledge base and RAG engine
        rag_engine = _get_rag_engine(vector_store_manager, conversation_manager, config)
        
        # Main content area
        _render_main_content(vector_store_manager, rag_engine, conversation_manager, config)
        
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        logger.error(f"Application error: {str(e)}", exc_info=True)


def _initialize_session_state() -> None:
    """Initialize Streamlit session state variables."""
    defaults = {
        "selected_kb": None,
        "current_page": "chat",
        "app_initialized": False,
        "vector_store_manager": None,
        "conversation_manager": None,
        "rag_engine": None
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def _render_api_key_setup() -> None:
    """Render API key setup interface."""
    st.title("🔑 Setup Required")
    st.error("OpenAI API key is required to use this application.")
    
    st.markdown("""
    ### How to set up your OpenAI API key:
    
    1. **Get your API key** from [OpenAI Platform](https://platform.openai.com/api-keys)
    2. **Create a `.env` file** in the project root directory
    3. **Add your API key** to the `.env` file:
       ```
       OPENAI_API_KEY=your_api_key_here
       ```
    4. **Restart the application**
    
    ### Security Note
    - Never share your API key publicly
    - Keep your `.env` file out of version control
    - Monitor your API usage on the OpenAI platform
    """)


def _get_vector_store_manager(config) -> VectorStoreManager:
    """Get or create vector store manager instance."""
    if "vector_store_manager" not in st.session_state or st.session_state.vector_store_manager is None:
        try:
            st.session_state.vector_store_manager = VectorStoreManager(config)
            logger.info("Initialized VectorStoreManager")
        except Exception as e:
            st.error(f"Failed to initialize vector store manager: {str(e)}")
            logger.error(f"Failed to initialize vector store manager: {str(e)}")
            st.stop()
    
    return st.session_state.vector_store_manager


def _get_conversation_manager(config) -> ConversationManager:
    """Get or create conversation manager instance."""
    if "conversation_manager" not in st.session_state or st.session_state.conversation_manager is None:
        try:
            st.session_state.conversation_manager = ConversationManager(config)
            logger.info("Initialized ConversationManager")
        except Exception as e:
            st.error(f"Failed to initialize conversation manager: {str(e)}")
            logger.error(f"Failed to initialize conversation manager: {str(e)}")
            st.stop()
    
    return st.session_state.conversation_manager


def _get_rag_engine(
    vector_store_manager: VectorStoreManager,
    conversation_manager: ConversationManager,
    config
) -> Optional[RAGEngine]:
    """Get or create RAG engine instance based on selected knowledge base."""
    selected_kb = st.session_state.get("selected_kb")
    
    if not selected_kb:
        return None
    
    # Check if we need to create a new RAG engine
    if (st.session_state.get("rag_engine") is None or 
        st.session_state.get("current_kb") != selected_kb):
        
        try:
            # Get the vector store for the selected knowledge base
            vector_store = vector_store_manager.get_knowledge_base(selected_kb)
            
            if vector_store is None:
                st.error(f"Could not load knowledge base: {selected_kb}")
                return None
            
            # Create RAG engine
            rag_engine = RAGEngine(vector_store, conversation_manager, config)
            
            # Store in session state
            st.session_state.rag_engine = rag_engine
            st.session_state.current_kb = selected_kb
            
            logger.info(f"Created RAG engine for knowledge base: {selected_kb}")
            
        except Exception as e:
            st.error(f"Failed to create RAG engine: {str(e)}")
            logger.error(f"Failed to create RAG engine: {str(e)}")
            return None
    
    return st.session_state.get("rag_engine")


def _render_sidebar(
    vector_store_manager: VectorStoreManager,
    conversation_manager: ConversationManager
) -> None:
    """Render the sidebar with navigation and controls."""
    with st.sidebar:
        st.title("🤖 RAG Chatbot")
        st.markdown("---")
        
        # Navigation
        st.subheader("📋 Navigation")
        current_page = st.radio(
            "Choose a page:",
            ["💬 Chat", "📄 Upload Documents"],
            index=0 if st.session_state.current_page == "chat" else 1,
            key="page_selector"
        )
        
        # Update current page
        if current_page == "💬 Chat":
            st.session_state.current_page = "chat"
        else:
            st.session_state.current_page = "upload"
        
        st.markdown("---")
        
        # Knowledge base selection
        st.subheader("📚 Knowledge Base")
        
        # Get available knowledge bases
        available_kbs = get_available_knowledge_bases(vector_store_manager)
        
        if available_kbs:
            selected_kb = st.selectbox(
                "Select knowledge base:",
                [""] + available_kbs,
                index=0 if st.session_state.selected_kb not in available_kbs else available_kbs.index(st.session_state.selected_kb) + 1,
                key="kb_selector",
                help="Choose a knowledge base to chat with"
            )
            
            # Update selected knowledge base
            if selected_kb and selected_kb != st.session_state.selected_kb:
                st.session_state.selected_kb = selected_kb
                # Clear existing RAG engine to force recreation
                st.session_state.rag_engine = None
                st.session_state.current_kb = None
                # Clear conversation when switching knowledge bases
                conversation_manager.clear_conversation()
                if "messages" in st.session_state:
                    st.session_state.messages = []
                st.rerun()
            
            if selected_kb:
                # Show knowledge base stats
                try:
                    kb_stats = vector_store_manager.get_knowledge_base_stats(selected_kb)
                    if kb_stats:
                        st.success(f"✅ {kb_stats['document_count']} documents loaded")
                except Exception as e:
                    st.warning(f"Could not get KB stats: {str(e)}")
        else:
            st.info("No knowledge bases available. Upload some documents first!")
            st.session_state.selected_kb = None
        
        st.markdown("---")
        
        # Chat controls (only show on chat page)
        if st.session_state.current_page == "chat":
            show_stats = render_chat_controls()
        
        st.markdown("---")
        
        # Application info
        st.subheader("ℹ️ About")
        st.caption("RAG Chatbot Platform v1.0")
        st.caption("Powered by LangChain & OpenAI")
        
        # Show current configuration
        with st.expander("🔧 Configuration"):
            config = get_config()
            st.write(f"**Model:** {config.openai_model}")
            st.write(f"**Chunk Size:** {config.chunk_size}")
            st.write(f"**Memory Limit:** {config.max_conversation_history}")
            st.write(f"**Max File Size:** {config.max_file_size_mb}MB")


def _render_main_content(
    vector_store_manager: VectorStoreManager,
    rag_engine: Optional[RAGEngine],
    conversation_manager: ConversationManager,
    config
) -> None:
    """Render the main content area based on current page."""
    
    # Application header
    st.title("🤖 RAG Chatbot Platform")
    st.markdown("Upload documents, create knowledge bases, and chat with your data using AI.")
    
    # Render content based on current page
    if st.session_state.current_page == "chat":
        render_chat_interface(rag_engine, conversation_manager, config)
    
    elif st.session_state.current_page == "upload":
        render_document_upload(vector_store_manager, config)
    
    # Footer
    st.markdown("---")
    with st.expander("🛠️ System Status"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            kb_count = len(get_available_knowledge_bases(vector_store_manager))
            st.metric("Knowledge Bases", kb_count)
        
        with col2:
            selected_kb = st.session_state.get("selected_kb", "None")
            if selected_kb and selected_kb != "None":
                kb_stats = vector_store_manager.get_knowledge_base_stats(selected_kb)
                doc_count = kb_stats['document_count'] if kb_stats else 0
            else:
                doc_count = 0
            st.metric("Documents in Current KB", doc_count)
        
        with col3:
            conversation_active = len(st.session_state.get("messages", [])) > 0
            st.metric("Chat Active", "Yes" if conversation_active else "No")


if __name__ == "__main__":
    main()