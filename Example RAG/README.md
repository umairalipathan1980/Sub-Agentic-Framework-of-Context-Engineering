# RAG Chatbot Platform

A production-ready Streamlit-based Retrieval-Augmented Generation (RAG) chatbot platform that enables users to upload PDF documents, create knowledge bases, and have intelligent conversations with their documents using OpenAI APIs and Chroma vector database.

## Features

- 🤖 **ChatGPT-like Interface**: Professional conversational UI with streaming responses
- 📄 **PDF Document Processing**: Upload and process PDF documents with automatic chunking
- 🧠 **Knowledge Base Management**: Create, switch, and manage multiple knowledge bases
- 💬 **Conversation Memory**: Maintains 3-message conversation history for context
- 🔍 **Semantic Search**: RAG implementation with vector similarity search
- 🏗️ **Modular Architecture**: Clean separation between UI and core logic for scalability

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Setup Steps

1. **Clone and setup the project:**
   ```bash
   git clone <your-repo-url>
   cd trial-repo
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your environment:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

5. **Access the application:**
   Open your browser to `http://localhost:8501`

## Usage

### Creating a Knowledge Base

1. Navigate to the "📄 Upload Documents" section
2. Choose "Create new knowledge base" 
3. Enter a name for your knowledge base
4. Upload one or more PDF files (max 200MB per file)
5. Click "🚀 Process Documents" to create the knowledge base

### Chatting with Documents

1. Select a knowledge base from the sidebar dropdown
2. Go to the "💬 Chat" section
3. Ask questions about your documents
4. The AI will provide contextual answers based on the document content
5. Conversation history is maintained for follow-up questions

### Managing Knowledge Bases

- **Switch Knowledge Bases**: Use the sidebar dropdown to switch between different document collections
- **Add Documents**: Upload additional PDFs to existing knowledge bases
- **Delete Knowledge Bases**: Remove knowledge bases you no longer need
- **View Statistics**: See document counts and processing details

## Architecture

```
src/
├── application/          # UI layer (Streamlit interfaces)
│   ├── streamlit_app.py  # Main application
│   ├── chat_interface.py # Chat UI components
│   └── document_upload.py# PDF upload interface
├── core/                 # Business logic layer
│   ├── rag_engine.py     # RAG implementation
│   ├── document_processor.py # PDF processing
│   ├── vector_store.py   # Chroma integration
│   └── conversation_manager.py # Memory management
└── utils/
    └── config.py         # Configuration management
```

## Configuration

The application can be configured via environment variables in your `.env` file:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (with defaults)
OPENAI_MODEL=gpt-4
CHROMA_PERSIST_DIR=data/knowledge_bases
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_CONVERSATION_HISTORY=3
MAX_FILE_SIZE_MB=200
```

## Technical Details

### Document Processing
- Uses `PyPDFLoader` for robust PDF text extraction
- `RecursiveCharacterTextSplitter` with 1000-character chunks and 200-character overlap
- Automatic metadata preservation (filename, page numbers, processing timestamps)

### Vector Storage
- Chroma database for persistent vector storage
- OpenAI `text-embedding-3-small` for efficient embeddings
- Collection-based knowledge base isolation
- Local persistence in `data/knowledge_bases/`

### Conversation Management
- LangChain `ConversationBufferWindowMemory` with k=2 (3-message limit)
- Thread-based conversation tracking
- Session state management for UI persistence

### RAG Pipeline
- Top-4 semantic similarity retrieval
- Contextual prompt engineering with conversation history
- Streaming response generation for smooth user experience
- Error handling with graceful degradation

## Testing

Run the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run specific test modules
pytest tests/test_document_processor.py -v
pytest tests/test_vector_store.py -v
pytest tests/test_rag_engine.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

Validate project structure:

```bash
python validate_structure.py
```

## Performance Considerations

- **Memory Management**: Chunked PDF processing prevents memory issues with large files
- **Vector Search**: Optimized k=4 retrieval balances relevance and performance  
- **Streaming**: Async response generation for responsive UI
- **Persistence**: Local Chroma storage eliminates database setup complexity

## Security

- 🔐 API keys managed via environment variables
- 📁 Local file processing with automatic cleanup
- 🛡️ Input validation for file types and sizes
- 🚫 No external data transmission (documents stay local)

## Troubleshooting

### Common Issues

1. **"No module named 'pydantic'" or similar dependency errors**
   - Ensure you've installed all requirements: `pip install -r requirements.txt`

2. **"OpenAI API key is required" error**
   - Check your `.env` file has the correct `OPENAI_API_KEY` value
   - Restart the application after updating `.env`

3. **"Failed to initialize vector store manager" error**
   - Ensure the `data/` directories exist and are writable
   - Check disk space for vector database storage

4. **PDF processing fails**
   - Verify PDF files are not corrupted or password-protected
   - Check file size is under the configured limit (default 200MB)
   - Ensure sufficient memory for large documents

5. **Slow response generation**
   - Check your OpenAI API rate limits and usage
   - Consider using `gpt-3.5-turbo` for faster responses
   - Reduce chunk retrieval count in RAG engine settings

### Getting Help

- Check the application logs in the terminal for detailed error messages
- Use the "📊 Show Statistics" feature to debug conversation and engine state
- Validate your setup with `python validate_structure.py`

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Ensure all tests pass: `pytest tests/`
5. Submit a pull request

## License

This project is provided as-is for educational and development purposes.

## Acknowledgments

- Built with [LangChain](https://python.langchain.com/) for RAG implementation
- [Streamlit](https://streamlit.io/) for the web interface
- [Chroma](https://www.trychroma.com/) for vector database
- [OpenAI](https://openai.com/) for language model capabilities