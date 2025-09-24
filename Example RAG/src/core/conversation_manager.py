"""
Conversation memory management for the RAG chatbot.
Handles conversation history with configurable memory limits.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage

from utils.config import AppConfig

logger = logging.getLogger(__name__)


class ConversationManager:
    """Manages conversation memory and history for the RAG chatbot."""
    
    def __init__(self, config: Optional[AppConfig] = None):
        """Initialize conversation manager with configuration."""
        if config is None:
            from utils.config import get_config
            config = get_config()
        
        self.config = config
        # Use k=2 to maintain last 2 exchanges (human + AI) = 3 total messages as per PRP
        self.memory_size = config.max_conversation_history - 1
        
        self.memory = ConversationBufferWindowMemory(
            k=self.memory_size,
            return_messages=True,
            memory_key="chat_history"
        )
        
        # Additional storage for session management
        self.session_messages: List[Dict[str, Any]] = []
        self.session_id: Optional[str] = None
        
        logger.info(f"Initialized ConversationManager with memory_size={self.memory_size}")
    
    def add_message(self, human_message: str, ai_message: str) -> None:
        """
        Add a human-AI message exchange to the conversation history.
        
        Args:
            human_message: The user's input message
            ai_message: The AI's response message
        """
        try:
            # Add to LangChain memory
            self.memory.chat_memory.add_user_message(human_message)
            self.memory.chat_memory.add_ai_message(ai_message)
            
            # Add to session messages for Streamlit display
            timestamp = datetime.now().isoformat()
            
            self.session_messages.extend([
                {
                    "role": "user",
                    "content": human_message,
                    "timestamp": timestamp
                },
                {
                    "role": "assistant", 
                    "content": ai_message,
                    "timestamp": timestamp
                }
            ])
            
            # Maintain the message limit for session messages
            max_messages = self.config.max_conversation_history
            if len(self.session_messages) > max_messages:
                # Remove oldest messages to maintain limit
                excess = len(self.session_messages) - max_messages
                self.session_messages = self.session_messages[excess:]
            
            logger.debug(f"Added message exchange. Total session messages: {len(self.session_messages)}")
            
        except Exception as e:
            logger.error(f"Error adding message to conversation history: {str(e)}")
    
    def get_conversation_history(self) -> List[BaseMessage]:
        """
        Get the current conversation history as LangChain messages.
        
        Returns:
            List of BaseMessage objects representing the conversation history
        """
        try:
            return self.memory.chat_memory.messages
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {str(e)}")
            return []
    
    def get_session_messages(self) -> List[Dict[str, Any]]:
        """
        Get the current session messages for Streamlit display.
        
        Returns:
            List of message dictionaries with role, content, and timestamp
        """
        return self.session_messages.copy()
    
    def get_context_for_rag(self) -> str:
        """
        Get formatted conversation context for RAG pipeline.
        
        Returns:
            Formatted string containing recent conversation history
        """
        try:
            messages = self.get_conversation_history()
            if not messages:
                return ""
            
            # Format messages for context
            context_parts = []
            for message in messages[-self.memory_size*2:]:  # Get recent messages only
                if isinstance(message, HumanMessage):
                    context_parts.append(f"Human: {message.content}")
                elif isinstance(message, AIMessage):
                    context_parts.append(f"Assistant: {message.content}")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error generating RAG context: {str(e)}")
            return ""
    
    def clear_conversation(self) -> None:
        """Clear all conversation history."""
        try:
            self.memory.clear()
            self.session_messages.clear()
            logger.info("Cleared conversation history")
        except Exception as e:
            logger.error(f"Error clearing conversation: {str(e)}")
    
    def set_session_id(self, session_id: str) -> None:
        """
        Set the session ID for this conversation.
        
        Args:
            session_id: Unique identifier for the conversation session
        """
        self.session_id = session_id
        logger.debug(f"Set session ID: {session_id}")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current conversation state.
        
        Returns:
            Dictionary containing conversation statistics and metadata
        """
        try:
            langchain_messages = self.get_conversation_history()
            
            return {
                "session_id": self.session_id,
                "total_session_messages": len(self.session_messages),
                "total_langchain_messages": len(langchain_messages),
                "memory_limit": self.config.max_conversation_history,
                "langchain_memory_size": self.memory_size,
                "last_update": datetime.now().isoformat() if self.session_messages else None,
                "conversation_active": len(self.session_messages) > 0
            }
            
        except Exception as e:
            logger.error(f"Error generating conversation summary: {str(e)}")
            return {"error": str(e)}
    
    def load_session_messages(self, messages: List[Dict[str, Any]]) -> None:
        """
        Load messages from a previous session.
        
        Args:
            messages: List of message dictionaries to load
        """
        try:
            self.clear_conversation()
            
            # Rebuild conversation history
            user_messages = []
            ai_messages = []
            
            for msg in messages:
                if msg["role"] == "user":
                    user_messages.append(msg["content"])
                elif msg["role"] == "assistant":
                    ai_messages.append(msg["content"])
            
            # Add message pairs to maintain conversation flow
            min_length = min(len(user_messages), len(ai_messages))
            for i in range(min_length):
                self.add_message(user_messages[i], ai_messages[i])
            
            # Handle any remaining messages
            if len(user_messages) > min_length:
                # There's a pending user message without AI response
                self.memory.chat_memory.add_user_message(user_messages[-1])
                self.session_messages.append({
                    "role": "user",
                    "content": user_messages[-1],
                    "timestamp": datetime.now().isoformat()
                })
            
            logger.info(f"Loaded {len(messages)} messages into conversation history")
            
        except Exception as e:
            logger.error(f"Error loading session messages: {str(e)}")
    
    def add_user_message(self, message: str) -> None:
        """
        Add only a user message (used when waiting for AI response).
        
        Args:
            message: The user's input message
        """
        try:
            self.memory.chat_memory.add_user_message(message)
            
            self.session_messages.append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Maintain message limit
            if len(self.session_messages) > self.config.max_conversation_history:
                self.session_messages = self.session_messages[1:]
            
            logger.debug(f"Added user message. Total session messages: {len(self.session_messages)}")
            
        except Exception as e:
            logger.error(f"Error adding user message: {str(e)}")
    
    def add_ai_message(self, message: str) -> None:
        """
        Add only an AI message (used after generating response).
        
        Args:
            message: The AI's response message
        """
        try:
            self.memory.chat_memory.add_ai_message(message)
            
            self.session_messages.append({
                "role": "assistant",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Maintain message limit
            if len(self.session_messages) > self.config.max_conversation_history:
                self.session_messages = self.session_messages[1:]
            
            logger.debug(f"Added AI message. Total session messages: {len(self.session_messages)}")
            
        except Exception as e:
            logger.error(f"Error adding AI message: {str(e)}")
    
    def get_last_user_message(self) -> Optional[str]:
        """
        Get the last user message from the conversation.
        
        Returns:
            The last user message content, or None if no user messages exist
        """
        for message in reversed(self.session_messages):
            if message["role"] == "user":
                return message["content"]
        return None