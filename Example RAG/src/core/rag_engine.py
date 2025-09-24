"""
RAG (Retrieval-Augmented Generation) engine implementation.
Combines document retrieval with language model generation for contextual responses.
"""

import logging
from typing import AsyncIterator, Optional, List, Dict, Any
import asyncio

from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain

from core.conversation_manager import ConversationManager
from utils.config import AppConfig

logger = logging.getLogger(__name__)


class RAGEngine:
    """RAG engine that combines document retrieval with conversational AI."""
    
    def __init__(
        self, 
        vector_store: Chroma, 
        conversation_manager: ConversationManager,
        config: Optional[AppConfig] = None
    ):
        """
        Initialize RAG engine with vector store and conversation manager.
        
        Args:
            vector_store: Chroma vector store for document retrieval
            conversation_manager: Manager for conversation history
            config: Application configuration
        """
        if config is None:
            from utils.config import get_config
            config = get_config()
        
        self.config = config
        self.vector_store = vector_store
        self.conversation_manager = conversation_manager
        
        # Initialize OpenAI Chat model with streaming
        self.llm = ChatOpenAI(
            model=config.openai_model,
            openai_api_key=config.openai_api_key,
            streaming=True,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Configure retriever
        self.retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4}  # Retrieve top 4 most relevant chunks
        )
        
        # Create conversational retrieval chain
        self._setup_retrieval_chain()
        
        logger.info("Initialized RAG engine with conversational retrieval")
    
    def _setup_retrieval_chain(self) -> None:
        """Set up the conversational retrieval chain."""
        # Custom prompt template for RAG responses
        prompt_template = """You are a helpful AI assistant that answers questions based on the provided context and conversation history.

Context from documents:
{context}

Conversation history:
{chat_history}

Current question: {question}

Instructions:
1. Use the provided context to answer the question accurately
2. If the context doesn't contain relevant information, output the following verbatim: "No relevant information found." 
3. Maintain conversation context from the history
4. Be concise but comprehensive in your response
5. If asked about previous parts of the conversation, refer to the chat history

Answer:"""

        self.prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "chat_history", "question"]
        )
        
        # Create the conversational retrieval chain
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.retriever,
            memory=self.conversation_manager.memory,
            return_source_documents=True,
            verbose=True
        )
        
        logger.info("Set up conversational retrieval chain")
    
    async def generate_response(self, question: str) -> AsyncIterator[str]:
        """
        Generate a streaming response to a question using RAG.
        
        Args:
            question: User's question
            
        Yields:
            String chunks of the response as they're generated
        """
        try:
            logger.info(f"Generating RAG response for question: {question[:100]}...")
            
            # Get relevant documents
            relevant_docs = await self._retrieve_documents(question)
            
            # Prepare context from retrieved documents
            context = self._prepare_context(relevant_docs)
            
            # Get conversation history
            chat_history = self.conversation_manager.get_context_for_rag()
            
            # Generate response using streaming
            response = ""
            async for chunk in self._stream_llm_response(question, context, chat_history):
                response += chunk
                yield chunk
            
            # Add the complete exchange to conversation memory
            self.conversation_manager.add_message(question, response)
            
            logger.info(f"Generated response with {len(relevant_docs)} source documents")
            
        except Exception as e:
            logger.error(f"Error generating RAG response: {str(e)}")
            error_message = f"I apologize, but I encountered an error while generating a response: {str(e)}"
            yield error_message
            
            # Still add to conversation history for continuity
            self.conversation_manager.add_message(question, error_message)
    
    async def _retrieve_documents(self, question: str) -> List[Document]:
        """
        Retrieve relevant documents for the question.
        
        Args:
            question: User's question
            
        Returns:
            List of relevant documents
        """
        try:
            # Use async retrieval if available
            if hasattr(self.retriever, 'aget_relevant_documents'):
                return await self.retriever.aget_relevant_documents(question)
            else:
                # Fallback to sync retrieval (run in thread pool)
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(
                    None, 
                    self.retriever.get_relevant_documents, 
                    question
                )
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            return []
    
    def _prepare_context(self, documents: List[Document]) -> str:
        """
        Prepare context string from retrieved documents.
        
        Args:
            documents: Retrieved documents
            
        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant context found in the knowledge base."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            # Include document metadata if available
            source = doc.metadata.get('source', f'Document {i}')
            page = doc.metadata.get('page', '')
            page_info = f" (Page {page})" if page else ""
            
            context_parts.append(f"[Source {i} - {source}{page_info}]:\n{doc.page_content}\n")
        
        return "\n".join(context_parts)
    
    async def _stream_llm_response(
        self, 
        question: str, 
        context: str, 
        chat_history: str
    ) -> AsyncIterator[str]:
        """
        Stream response from the language model.
        
        Args:
            question: User's question
            context: Retrieved document context
            chat_history: Conversation history
            
        Yields:
            String chunks of the response
        """
        try:
            # Format the prompt
            formatted_prompt = self.prompt.format(
                question=question,
                context=context,
                chat_history=chat_history
            )
            
            # Stream the response
            async for chunk in self.llm.astream(formatted_prompt):
                if hasattr(chunk, 'content'):
                    yield chunk.content
                else:
                    yield str(chunk)
                    
        except Exception as e:
            logger.error(f"Error streaming LLM response: {str(e)}")
            yield f"Error generating response: {str(e)}"
    
    def get_source_documents(self, question: str) -> List[Document]:
        """
        Get source documents for a question (synchronous version for debugging).
        
        Args:
            question: User's question
            
        Returns:
            List of relevant documents
        """
        try:
            return self.retriever.get_relevant_documents(question)
        except Exception as e:
            logger.error(f"Error getting source documents: {str(e)}")
            return []
    
    def update_vector_store(self, vector_store: Chroma) -> None:
        """
        Update the vector store used by the RAG engine.
        
        Args:
            vector_store: New vector store to use
        """
        self.vector_store = vector_store
        self.retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4}
        )
        
        # Update the retrieval chain
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.retriever,
            memory=self.conversation_manager.memory,
            return_source_documents=True,
            verbose=True
        )
        
        logger.info("Updated RAG engine with new vector store")
    
    def get_engine_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG engine.
        
        Returns:
            Dictionary containing engine statistics
        """
        try:
            # Get vector store stats
            collection = self.vector_store._collection
            doc_count = collection.count() if collection else 0
            
            # Get conversation stats
            conversation_stats = self.conversation_manager.get_conversation_summary()
            
            return {
                "model": self.config.openai_model,
                "vector_store_documents": doc_count,
                "retriever_k": self.retriever.search_kwargs.get("k", 0),
                "conversation_active": conversation_stats.get("conversation_active", False),
                "total_messages": conversation_stats.get("total_session_messages", 0),
                "memory_limit": self.config.max_conversation_history
            }
            
        except Exception as e:
            logger.error(f"Error getting engine stats: {str(e)}")
            return {"error": str(e)}