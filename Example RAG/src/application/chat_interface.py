"""
Chat interface for the Streamlit RAG chatbot platform.
Provides a ChatGPT-like conversational experience with streaming responses.
"""

import streamlit as st
import asyncio
import logging
from typing import Optional, AsyncIterator
import time

from core.rag_engine import RAGEngine
from core.conversation_manager import ConversationManager
from utils.config import AppConfig, get_config

logger = logging.getLogger(__name__)


def render_chat_interface(
    rag_engine: Optional[RAGEngine] = None,
    conversation_manager: Optional[ConversationManager] = None,
    config: Optional[AppConfig] = None
) -> None:
    """
    Render the main chat interface.
    
    Args:
        rag_engine: RAG engine for generating responses
        conversation_manager: Conversation manager for history
        config: Application configuration
    """
    if config is None:
        config = get_config()
    
    # Initialize session state for chat messages
    _initialize_chat_session_state()
    
    if not rag_engine:
        st.warning("⚠️ Please select a knowledge base to start chatting.")
        st.info("Go to the 'Upload Documents' section to create a knowledge base, or select an existing one from the sidebar.")
        return
    
    # Display chat header
    st.header("💬 Chat with your documents")
    
    # Show knowledge base info
    try:
        engine_stats = rag_engine.get_engine_stats()
        st.caption(f"📚 Knowledge base loaded with {engine_stats.get('vector_store_documents', 0)} document chunks • "
                  f"Model: {engine_stats.get('model', 'Unknown')}")
    except Exception as e:
        logger.warning(f"Could not get engine stats: {e}")
    
    # Display chat history
    _display_chat_history()
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message to session state immediately
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt,
            "timestamp": time.time()
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # Create a simple synchronous generator for streaming
                def get_sync_response():
                    async def collect_response():
                        chunks = []
                        async for chunk in rag_engine.generate_response(prompt):
                            chunks.append(chunk)
                        return chunks
                    
                    return asyncio.run(collect_response())
                
                response_chunks = get_sync_response()
                
                # Display chunks with typing effect
                for chunk in response_chunks:
                    full_response += chunk
                    # Update the placeholder with current response + cursor
                    message_placeholder.markdown(full_response + "▌")
                    time.sleep(0.02)  # Small delay for smooth typing effect
                
                # Final update without cursor
                message_placeholder.markdown(full_response)
                
                # Add assistant response to session state
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": full_response,
                    "timestamp": time.time()
                })
                
            except Exception as e:
                error_message = f"I apologize, but I encountered an error: {str(e)}"
                message_placeholder.markdown(error_message)
                
                # Add error message to session state
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": error_message,
                    "timestamp": time.time()
                })
                
                logger.error(f"Error in chat interface: {str(e)}")
    
    # Display conversation statistics in sidebar
    if st.sidebar.checkbox("📊 Show conversation stats"):
        _display_conversation_stats(conversation_manager, rag_engine)


def _initialize_chat_session_state() -> None:
    """Initialize session state variables for chat interface."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "chat_started" not in st.session_state:
        st.session_state.chat_started = False
    
    if "current_session_id" not in st.session_state:
        import uuid
        st.session_state.current_session_id = str(uuid.uuid4())


def _display_chat_history() -> None:
    """Display the chat message history."""
    # Display all messages from session state
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


async def _get_streaming_response(rag_engine: RAGEngine, prompt: str) -> AsyncIterator[str]:
    """
    Get streaming response from RAG engine.
    
    Args:
        rag_engine: RAG engine to generate response
        prompt: User's input prompt
        
    Yields:
        String chunks of the response
    """
    try:
        async for chunk in rag_engine.generate_response(prompt):
            yield chunk
    except Exception as e:
        logger.error(f"Error getting streaming response: {str(e)}")
        yield f"Error generating response: {str(e)}"


def _display_conversation_stats(
    conversation_manager: Optional[ConversationManager],
    rag_engine: Optional[RAGEngine]
) -> None:
    """
    Display conversation and engine statistics in the sidebar.
    
    Args:
        conversation_manager: Conversation manager instance
        rag_engine: RAG engine instance
    """
    st.sidebar.subheader("💬 Conversation Stats")
    
    try:
        # Session message count
        message_count = len(st.session_state.get('messages', []))
        user_messages = len([m for m in st.session_state.get('messages', []) if m['role'] == 'user'])
        ai_messages = len([m for m in st.session_state.get('messages', []) if m['role'] == 'assistant'])
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("Total Messages", message_count)
        with col2:
            st.metric("Exchanges", user_messages)
        
        # Conversation manager stats
        if conversation_manager:
            try:
                conv_stats = conversation_manager.get_conversation_summary()
                st.sidebar.write("**Memory Status:**")
                st.sidebar.write(f"• LangChain messages: {conv_stats.get('total_langchain_messages', 0)}")
                st.sidebar.write(f"• Session messages: {conv_stats.get('total_session_messages', 0)}")
                st.sidebar.write(f"• Memory limit: {conv_stats.get('memory_limit', 0)}")
                st.sidebar.write(f"• Active: {'Yes' if conv_stats.get('conversation_active', False) else 'No'}")
            except Exception as e:
                st.sidebar.error(f"Error getting conversation stats: {str(e)}")
        
        # RAG engine stats
        if rag_engine:
            try:
                engine_stats = rag_engine.get_engine_stats()
                st.sidebar.write("**RAG Engine:**")
                st.sidebar.write(f"• Model: {engine_stats.get('model', 'Unknown')}")
                st.sidebar.write(f"• Documents: {engine_stats.get('vector_store_documents', 0)}")
                st.sidebar.write(f"• Retriever K: {engine_stats.get('retriever_k', 0)}")
            except Exception as e:
                st.sidebar.error(f"Error getting engine stats: {str(e)}")
        
        # Session info
        st.sidebar.write("**Session:**")
        st.sidebar.write(f"• ID: {st.session_state.get('current_session_id', 'Unknown')[:8]}...")
        
        if st.session_state.get('messages'):
            first_message_time = min(m.get('timestamp', time.time()) for m in st.session_state.messages)
            duration = time.time() - first_message_time
            st.sidebar.write(f"• Duration: {duration/60:.1f} min")
        
    except Exception as e:
        st.sidebar.error(f"Error displaying stats: {str(e)}")
        logger.error(f"Error displaying conversation stats: {str(e)}")


def clear_chat_history() -> None:
    """Clear the chat history from session state."""
    if "messages" in st.session_state:
        st.session_state.messages = []
    
    if "chat_started" in st.session_state:
        st.session_state.chat_started = False
    
    # Generate new session ID
    import uuid
    st.session_state.current_session_id = str(uuid.uuid4())
    
    logger.info("Cleared chat history")


def export_chat_history() -> Optional[str]:
    """
    Export chat history as a formatted string.
    
    Returns:
        Formatted chat history or None if no messages
    """
    messages = st.session_state.get('messages', [])
    if not messages:
        return None
    
    try:
        import datetime
        export_lines = [
            "# Chat Export",
            f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Session ID: {st.session_state.get('current_session_id', 'Unknown')}",
            f"Total Messages: {len(messages)}",
            "",
        ]
        
        for i, message in enumerate(messages, 1):
            role = "🧑 User" if message['role'] == 'user' else "🤖 Assistant"
            timestamp = message.get('timestamp', time.time())
            timestamp_str = datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
            
            export_lines.extend([
                f"## Message {i} - {role} ({timestamp_str})",
                "",
                message['content'],
                "",
            ])
        
        return "\n".join(export_lines)
        
    except Exception as e:
        logger.error(f"Error exporting chat history: {str(e)}")
        return None


def load_chat_history(
    conversation_manager: ConversationManager,
    messages: list
) -> bool:
    """
    Load chat history into the conversation manager and session state.
    
    Args:
        conversation_manager: Conversation manager to load into
        messages: List of message dictionaries
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Clear current state
        clear_chat_history()
        
        # Load into session state
        st.session_state.messages = messages.copy()
        st.session_state.chat_started = len(messages) > 0
        
        # Load into conversation manager
        conversation_manager.load_session_messages(messages)
        
        logger.info(f"Loaded {len(messages)} messages into chat history")
        return True
        
    except Exception as e:
        logger.error(f"Error loading chat history: {str(e)}")
        return False


def render_chat_controls() -> None:
    """Render chat control buttons in the sidebar."""
    st.sidebar.subheader("💬 Chat Controls")
    
    # Clear chat button
    if st.sidebar.button("🗑️ Clear Chat", help="Clear all chat messages"):
        clear_chat_history()
        st.sidebar.success("Chat history cleared!")
        st.rerun()
    
    # Export chat button
    if st.sidebar.button("📥 Export Chat", help="Export chat history as text"):
        exported_chat = export_chat_history()
        if exported_chat:
            st.sidebar.download_button(
                label="📄 Download Chat History",
                data=exported_chat,
                file_name=f"chat_export_{int(time.time())}.md",
                mime="text/markdown",
                help="Download your chat history as a Markdown file"
            )
        else:
            st.sidebar.info("No chat history to export")
    
    # Chat statistics toggle
    return st.sidebar.checkbox("📊 Show Statistics", help="Display detailed chat and engine statistics")