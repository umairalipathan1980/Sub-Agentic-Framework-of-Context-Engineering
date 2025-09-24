"""
Configuration management for the RAG Chatbot Platform.
Handles environment variables and application settings.
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Application configuration with environment variable support."""
    
    # OpenAI API configuration
    openai_api_key: str = Field(..., description="OpenAI API key for LLM access")
    openai_model: str = Field(default="gpt-4", description="OpenAI model to use")
    
    # Chroma vector database settings
    chroma_persist_dir: str = Field(
        default="data/knowledge_bases", 
        description="Directory for Chroma database persistence"
    )
    
    # Document processing parameters
    chunk_size: int = Field(default=1000, description="Text chunk size for document splitting")
    chunk_overlap: int = Field(default=200, description="Overlap between text chunks")
    
    # Conversation management
    max_conversation_history: int = Field(
        default=3, 
        description="Maximum number of messages to maintain in conversation history"
    )
    
    # File upload settings
    upload_dir: str = Field(default="data/uploads", description="Temporary upload directory")
    max_file_size_mb: int = Field(default=200, description="Maximum file size in MB")
    
    # Streamlit settings
    page_title: str = Field(default="RAG Chatbot Platform", description="Page title for Streamlit app")
    page_layout: str = Field(default="wide", description="Page layout for Streamlit app")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


def get_config() -> AppConfig:
    """Get application configuration instance."""
    return AppConfig()


def ensure_directories_exist(config: AppConfig) -> None:
    """Ensure required directories exist, create if they don't."""
    directories = [
        config.chroma_persist_dir,
        config.upload_dir
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)