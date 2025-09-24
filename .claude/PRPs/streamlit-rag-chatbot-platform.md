# Streamlit RAG Chatbot Platform PRP

## Goal
- **Feature Goal:** Build a production-ready Streamlit-based RAG chatbot platform that enables users to upload PDF documents, create knowledge bases, and have intelligent conversations with their documents using OpenAI APIs and Chroma vector database
- **Deliverable:** Complete web application with document processing, vector storage, conversational memory, and professional ChatGPT-like UI
- **Success Definition:** Users can upload PDFs, switch between knowledge bases, ask questions about document contents, and receive contextual answers with 3-message conversation history

## User Persona
- **Target User:** Knowledge workers, researchers, students, and professionals who need to interact with and extract insights from document collections
- **Use Case:** Uploading research papers, manuals, reports, or documentation and asking specific questions to find relevant information quickly
- **User Journey:** 
  1. Launch application → Select/create knowledge base → Upload PDFs → Ask questions → Receive contextual answers → Switch knowledge bases as needed
- **Pain Points Addressed:** Eliminates manual document searching, provides instant access to document insights, maintains conversation context for follow-up questions

## Why
- Enables rapid document analysis and insight extraction through natural language queries
- Provides scalable knowledge base management for different document collections
- Integrates with OpenAI's latest models for high-quality response generation
- Offers production-ready architecture with clean separation of concerns

## What
**User-Visible Features:**
- Professional chat interface with streaming responses (ChatGPT-like)
- PDF document upload with progress indicators and validation
- Knowledge base selection dropdown with creation/switching capabilities
- Conversation history display with proper message threading
- Real-time document processing status and feedback
- Error handling with user-friendly messages

**Technical Requirements:**
- Streamlit frontend with st.chat_message() and st.chat_input() components
- LangChain integration for RAG pipeline and conversation management
- Chroma vector database for embeddings storage and semantic search
- OpenAI API integration for response generation
- PDF processing with chunking and vector embeddings
- Session state management for chat history and knowledge base context
- Modular architecture supporting future frontend migration

## Success Criteria
- [ ] Users can upload and process PDF documents successfully
- [ ] Knowledge base creation and switching works seamlessly
- [ ] Chat interface provides relevant, contextual responses
- [ ] Conversation memory maintains last 3 message exchanges
- [ ] Response streaming works smoothly without blocking
- [ ] All components handle errors gracefully with user feedback
- [ ] Application startup time under 10 seconds
- [ ] Document processing completes within reasonable time (under 2 minutes for 20-page PDF)

## All Needed Context

### Context Completeness Check
> **If someone knew nothing about this codebase, would they have everything needed to implement this successfully?**
✅ Yes - This PRP provides complete implementation blueprint with external documentation, code patterns, and step-by-step tasks.

### Documentation & References
**MUST READ — Include these in your context window**

- **url:** https://python.langchain.com/docs/tutorials/rag/  
  **why:** Core RAG architecture patterns - document loading, text splitting, vector embeddings, retrieval-generation workflow  
  **critical:** Use RecursiveCharacterTextSplitter with chunk_size=1000, chunk_overlap=200 for optimal performance

- **url:** https://python.langchain.com/docs/tutorials/qa_chat_history/  
  **why:** Conversational memory implementation patterns using message sequences and LangGraph MemorySaver  
  **critical:** Use thread-based persistence with unique conversation IDs for state management

- **url:** https://python.langchain.com/docs/integrations/vectorstores/chroma/  
  **why:** Chroma vector database integration patterns - persistence, document management, similarity search  
  **critical:** Install langchain-chroma>=0.1.2, use persist_directory for local storage

- **url:** https://docs.streamlit.io/develop/api-reference/chat  
  **why:** Chat component implementation - st.chat_message(), st.chat_input(), session state patterns  
  **critical:** Use st.session_state for chat history persistence across interactions

- **url:** https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps  
  **why:** Complete conversational app patterns including streaming responses and OpenAI integration  
  **critical:** Implement st.write_stream() for gradual response rendering with generator functions

- **url:** https://www.analyticsvidhya.com/blog/2024/04/rag-and-streamlit-chatbot-chat-with-documents-using-llm/  
  **why:** Production-ready architecture examples with session state management and document processing workflows  
  **critical:** Use ConversationBufferWindowMemory(k=2) for 3-message history (k=2 preserves last 2 exchanges = 3 total messages)

### Codebase Overview
**Current codebase tree:** Empty repository - fresh implementation required
```
/mnt/c/Users/h02317/trial-repo/
├── .claude/
│   ├── INITIAL.md
│   └── PRPs/
└── setup_claude_multi_agents_script.sh
```

**Desired codebase tree with files to be added:**
```
/mnt/c/Users/h02317/trial-repo/
├── src/
│   ├── application/          # UI layer
│   │   ├── __init__.py
│   │   ├── streamlit_app.py  # Main Streamlit interface
│   │   ├── chat_interface.py # Chat UI components
│   │   └── document_upload.py # PDF upload interface
│   ├── core/                 # Business logic layer
│   │   ├── __init__.py
│   │   ├── rag_engine.py     # RAG implementation
│   │   ├── document_processor.py # PDF processing
│   │   ├── vector_store.py   # Chroma integration
│   │   └── conversation_manager.py # Memory management
│   └── utils/
│       ├── __init__.py
│       └── config.py         # Configuration management
├── data/
│   ├── knowledge_bases/      # Chroma persistence directory
│   └── uploads/             # Temporary PDF storage
├── tests/
│   ├── test_rag_engine.py
│   ├── test_document_processor.py
│   └── test_vector_store.py
├── requirements.txt
├── .env.example
└── app.py                   # Application entry point
```

### Known Gotchas of Our Codebase & Library Quirks
- **CRITICAL:** LangChain v1.0 upcoming in October 2025 - use stable version langchain>=0.1.0,<1.0.0
- **CRITICAL:** Chroma requires langchain-chroma>=0.1.2 for proper integration
- **CRITICAL:** OpenAI API streaming requires langchain-openai package, not openai directly
- **CRITICAL:** Streamlit session_state must be initialized before use to avoid KeyError
- **CRITICAL:** PDF processing can consume significant memory - implement chunked processing for large files
- **CRITICAL:** Chroma persist_directory must exist before initialization - create directories programmatically

---

## Implementation Blueprint

### Data Models and Structure
Create core data structures for knowledge base management, document processing, and conversation state.

**Examples:**
- Knowledge base metadata models
- Document chunk representations
- Conversation message schemas
- Configuration classes

### Implementation Tasks (ordered by dependencies)

**Task 1: CREATE `src/utils/config.py`**
- **IMPLEMENT:** Configuration management with environment variables
- **INCLUDE:** OpenAI API key, Chroma settings, document processing parameters
- **PATTERN:** Use Pydantic BaseSettings for validation
```python
class AppConfig(BaseSettings):
    openai_api_key: str
    chroma_persist_dir: str = "data/knowledge_bases"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_conversation_history: int = 3
```
- **PLACEMENT:** `src/utils/config.py`

**Task 2: CREATE `src/core/document_processor.py`**
- **IMPLEMENT:** PDF processing with LangChain PyPDFLoader and RecursiveCharacterTextSplitter
- **FOLLOW pattern:** Analytics Vidhya tutorial architecture for document chunking
- **CRITICAL:** Implement error handling for corrupted PDFs and memory management for large files
```python
class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    
    async def process_pdf(self, file_path: str) -> List[Document]:
        # PDF loading, text extraction, chunking
        pass
```
- **DEPENDENCIES:** Configuration from Task 1
- **PLACEMENT:** `src/core/document_processor.py`

**Task 3: CREATE `src/core/vector_store.py`**
- **IMPLEMENT:** Chroma vector database integration with persistent storage
- **FOLLOW pattern:** LangChain Chroma integration documentation
- **CRITICAL:** Knowledge base isolation using collection names, proper persistence directory management
```python
class VectorStoreManager:
    def __init__(self, persist_directory: str):
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings()
    
    def create_knowledge_base(self, name: str, documents: List[Document]):
        # Create new Chroma collection
        pass
    
    def get_knowledge_base(self, name: str) -> Optional[Chroma]:
        # Load existing collection
        pass
```
- **DEPENDENCIES:** Document processor from Task 2
- **PLACEMENT:** `src/core/vector_store.py`

**Task 4: CREATE `src/core/conversation_manager.py`**
- **IMPLEMENT:** Conversation memory using LangChain ConversationBufferWindowMemory
- **FOLLOW pattern:** LangChain chat history tutorial with message-based state
- **CRITICAL:** Maintain exactly 3-message history (k=2 for ConversationBufferWindowMemory)
```python
class ConversationManager:
    def __init__(self, memory_size: int = 2):
        self.memory = ConversationBufferWindowMemory(
            k=memory_size,
            return_messages=True,
            memory_key="chat_history"
        )
    
    def add_message(self, human_message: str, ai_message: str):
        # Add to conversation history
        pass
```
- **DEPENDENCIES:** Configuration from Task 1
- **PLACEMENT:** `src/core/conversation_manager.py`

**Task 5: CREATE `src/core/rag_engine.py`**
- **IMPLEMENT:** RAG implementation using LangChain ConversationalRetrievalChain
- **FOLLOW pattern:** LangChain RAG tutorial architecture with retrieval-generation workflow
- **CRITICAL:** OpenAI integration with streaming support, contextual response generation
```python
class RAGEngine:
    def __init__(self, vector_store: Chroma, conversation_manager: ConversationManager):
        self.llm = ChatOpenAI(model="gpt-4", streaming=True)
        self.retriever = vector_store.as_retriever()
        self.conversation_manager = conversation_manager
        
    async def generate_response(self, question: str) -> AsyncIterator[str]:
        # RAG pipeline with streaming response
        pass
```
- **DEPENDENCIES:** Vector store manager (Task 3), conversation manager (Task 4)
- **PLACEMENT:** `src/core/rag_engine.py`

**Task 6: CREATE `src/application/document_upload.py`**
- **IMPLEMENT:** Streamlit file upload interface with PDF validation
- **FOLLOW pattern:** Streamlit file upload best practices with progress indicators
- **CRITICAL:** File type validation, size limits, temporary storage management
```python
def render_document_upload() -> Optional[str]:
    uploaded_file = st.file_uploader(
        "Upload PDF document",
        type="pdf",
        accept_multiple_files=False
    )
    
    if uploaded_file:
        # Save temporarily and return path
        pass
```
- **DEPENDENCIES:** Document processor from Task 2
- **PLACEMENT:** `src/application/document_upload.py`

**Task 7: CREATE `src/application/chat_interface.py`**
- **IMPLEMENT:** ChatGPT-like interface using st.chat_message() and st.chat_input()
- **FOLLOW pattern:** Streamlit conversational apps tutorial for session state and streaming
- **CRITICAL:** Session state management, streaming response display, proper message formatting
```python
def render_chat_interface(rag_engine: RAGEngine):
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Handle new input with streaming
    if prompt := st.chat_input("Ask a question about your documents"):
        # Process with RAG engine and stream response
        pass
```
- **DEPENDENCIES:** RAG engine from Task 5
- **PLACEMENT:** `src/application/chat_interface.py`

**Task 8: CREATE `src/application/streamlit_app.py`**
- **IMPLEMENT:** Main Streamlit application with knowledge base selection and page routing
- **FOLLOW pattern:** Streamlit multi-page app structure with sidebar navigation
- **CRITICAL:** Knowledge base dropdown, session state initialization, error boundary handling
```python
def main():
    st.set_page_config(page_title="RAG Chatbot Platform", layout="wide")
    
    # Sidebar: Knowledge base selection
    # Main area: Chat interface or document upload
    # Error handling and loading states
    pass
```
- **DEPENDENCIES:** Chat interface (Task 7), document upload (Task 6)
- **PLACEMENT:** `src/application/streamlit_app.py`

**Task 9: CREATE `app.py`**
- **IMPLEMENT:** Application entry point with initialization
- **FOLLOW pattern:** Standard Streamlit app entry point
- **CRITICAL:** Environment setup, directory creation, configuration loading
- **DEPENDENCIES:** Streamlit app from Task 8
- **PLACEMENT:** `app.py` (root level)

**Task 10: CREATE `requirements.txt`**
- **IMPLEMENT:** Complete dependency specification with pinned versions
- **CRITICAL:** LangChain compatibility, Streamlit version, OpenAI integration
```txt
streamlit>=1.28.0
langchain>=0.1.0,<1.0.0
langchain-chroma>=0.1.2
langchain-openai
chromadb
pypdf2
python-dotenv
pydantic
```
- **PLACEMENT:** `requirements.txt` (root level)

**Task 11: CREATE unit tests**
- **IMPLEMENT:** Test coverage for core components
- **FOLLOW pattern:** pytest with async support and mocking
- **COVERAGE:** Document processing, vector operations, conversation management
- **DEPENDENCIES:** All core modules
- **PLACEMENT:** `tests/` directory

---

## Implementation Patterns & Key Details

### PDF Processing Pattern
```python
async def process_pdf_upload(uploaded_file) -> List[Document]:
    # CRITICAL: Save to temporary location first
    temp_path = f"data/uploads/{uploaded_file.name}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getvalue())
    
    # PATTERN: Use PyPDFLoader for robust PDF handling
    loader = PyPDFLoader(temp_path)
    documents = await loader.aload()
    
    # GOTCHA: Clean up temporary file
    os.remove(temp_path)
    
    return documents
```

### Streamlit Session State Pattern
```python
def initialize_session_state():
    # CRITICAL: Initialize all session state variables
    defaults = {
        "messages": [],
        "current_knowledge_base": None,
        "knowledge_bases": [],
        "processing": False
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
```

### Streaming Response Pattern
```python
async def stream_rag_response(question: str, rag_engine: RAGEngine):
    # PATTERN: Generator function for Streamlit streaming
    response_placeholder = st.empty()
    full_response = ""
    
    async for chunk in rag_engine.generate_response(question):
        full_response += chunk
        response_placeholder.markdown(full_response + "▌")
    
    response_placeholder.markdown(full_response)
    return full_response
```

---

## Integration Points

**ENVIRONMENT:**
- **add to:** `.env`
- **pattern:** `OPENAI_API_KEY=sk-...`

**DIRECTORIES:**
- **create:** `data/knowledge_bases/` for Chroma persistence
- **create:** `data/uploads/` for temporary PDF storage

**STREAMLIT CONFIG:**
- **add to:** `.streamlit/config.toml`
- **pattern:** `maxUploadSize = 200` (MB limit for PDFs)

---

## Validation Loop

### Level 1: Syntax & Style (Immediate Feedback)
Run after each file creation — fix before proceeding.
```bash
# Install dependencies
pip install -r requirements.txt

# Format and lint
ruff check src/ --fix
mypy src/
ruff format src/

# Expected: Zero errors. If errors exist, READ output and fix before proceeding.
```

### Level 2: Unit Tests (Component Validation)
Test each component as it's created.
```bash
# Test individual components
pytest tests/test_document_processor.py -v
pytest tests/test_vector_store.py -v
pytest tests/test_rag_engine.py -v

# Full test suite
pytest tests/ -v --cov=src --cov-report=term-missing

# Expected: All tests pass with >80% coverage. Debug failures immediately.
```

### Level 3: Integration Testing (System Validation)
Application startup & functionality checks.
```bash
# Environment setup
cp .env.example .env
# Edit .env with actual OpenAI API key

# Create required directories
mkdir -p data/knowledge_bases data/uploads

# Start application
streamlit run app.py &
sleep 5  # Allow startup time

# Health check
curl -f http://localhost:8501/healthz || echo "Application health check failed"

# Manual testing checklist:
# 1. Upload a sample PDF document
# 2. Verify knowledge base creation
# 3. Ask questions and verify responses
# 4. Test knowledge base switching
# 5. Verify conversation history (3 messages)
# 6. Test error scenarios (invalid PDF, API failures)

# Expected: All functionality works, proper error handling, responsive UI
```

### Level 4: Creative & Domain-Specific Validation
```bash
# Performance Testing
# Test with various PDF sizes and complexity
python -c "
import time
from src.core.document_processor import DocumentProcessor
processor = DocumentProcessor()
start = time.time()
# Process sample PDF
print(f'Processing time: {time.time() - start:.2f}s')
"

# Memory Usage Testing
# Monitor memory consumption during document processing
python -m memory_profiler app.py

# RAG Quality Testing
# Test response relevance and accuracy
python -c "
from src.core.rag_engine import RAGEngine
# Test with known Q&A pairs
"

# Streamlit UI Testing
# Test responsive design and user experience
# Manual testing: resize browser, test mobile view

# Expected: Good performance, reasonable memory usage, high-quality responses
```

---

## Final Validation Checklist

### Technical Validation
- [ ] All 4 validation levels completed successfully
- [ ] All tests pass: `pytest tests/ -v`
- [ ] No linting errors: `ruff check src/`
- [ ] No type errors: `mypy src/`
- [ ] No formatting issues: `ruff format src/ --check`
- [ ] Application starts without errors: `streamlit run app.py`

### Feature Validation
- [ ] PDF upload and processing works correctly
- [ ] Knowledge base creation and management functions
- [ ] Chat interface displays properly with streaming responses
- [ ] Conversation memory maintains 3-message history
- [ ] Knowledge base switching preserves conversation state
- [ ] Error handling provides user-friendly messages
- [ ] Response quality meets user expectations

### Code Quality Validation
- [ ] Clean architecture with separated UI and core logic
- [ ] Modular design supporting future frontend migration
- [ ] Proper error handling throughout the application
- [ ] Configuration management through environment variables
- [ ] Comprehensive test coverage for core functionality
- [ ] Documentation and code comments where necessary

### User Experience Validation
- [ ] Professional ChatGPT-like interface
- [ ] Intuitive knowledge base selection and switching
- [ ] Clear feedback during document processing
- [ ] Responsive design works on different screen sizes
- [ ] Loading states and progress indicators function properly
- [ ] Error messages are helpful and actionable

---

## Anti-Patterns to Avoid
- ❌ Don't store API keys in code - use environment variables
- ❌ Don't load entire PDFs into memory - use chunked processing
- ❌ Don't skip error handling for OpenAI API rate limits
- ❌ Don't use synchronous operations in Streamlit - implement async patterns
- ❌ Don't mix UI logic with business logic - maintain clean separation
- ❌ Don't ignore session state initialization - always check and initialize
- ❌ Don't create new Chroma collections without checking existence first
- ❌ Don't forget to clean up temporary files after PDF processing

---

## Quality Score: 9/10
**Confidence Level:** Very High for one-pass implementation success

**Rationale:** This PRP provides comprehensive context including:
- Complete external documentation with specific URLs and critical insights
- Step-by-step implementation tasks with clear dependencies
- Practical code patterns from real-world examples
- Robust validation strategy with executable commands
- Clear architecture supporting scalability and maintainability
- Thorough error handling and edge case considerations

**Risk Factors:** Minimal - main risks are OpenAI API key setup and potential library version conflicts, both addressed in the PRP.