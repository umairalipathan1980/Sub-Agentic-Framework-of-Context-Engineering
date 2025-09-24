# RAG Chatbot Platform - Deployment Guide

## Quick Start

### 1. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env file and add your OpenAI API key:
# OPENAI_API_KEY=sk-your_actual_openai_key_here
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Application
```bash
streamlit run app.py
```

### 4. Access Application
Open your browser to: http://localhost:8501

## Application Structure

```
RAG Chatbot Platform/
├── app.py                    # Application entry point
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
├── README.md               # Full documentation
├── DEPLOYMENT.md           # This file
├── validate_structure.py   # Project validation
├── demo_test.py           # Core functionality test
│
├── .streamlit/
│   └── config.toml         # Streamlit configuration
│
├── src/                    # Source code
│   ├── application/        # UI layer
│   │   ├── streamlit_app.py    # Main Streamlit app
│   │   ├── chat_interface.py   # Chat UI components  
│   │   └── document_upload.py  # PDF upload interface
│   ├── core/              # Business logic
│   │   ├── rag_engine.py      # RAG implementation
│   │   ├── document_processor.py # PDF processing
│   │   ├── vector_store.py    # Chroma vector DB
│   │   └── conversation_manager.py # Chat memory
│   └── utils/
│       └── config.py      # Configuration management
│
├── tests/                 # Unit tests
│   ├── test_document_processor.py
│   ├── test_vector_store.py
│   └── test_rag_engine.py
│
└── data/                  # Data storage (auto-created)
    ├── knowledge_bases/   # Chroma vector database
    └── uploads/          # Temporary PDF storage
```

## Validation Commands

### Project Structure Validation
```bash
python validate_structure.py
```

### Core Component Testing (without dependencies)
```bash
python demo_test.py
```

### Unit Tests (requires dependencies)
```bash
pytest tests/ -v
```

## Configuration Options

All configuration via `.env` file:

```env
# Required
OPENAI_API_KEY=your_key_here

# Optional (with defaults shown)
OPENAI_MODEL=gpt-4
CHROMA_PERSIST_DIR=data/knowledge_bases  
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_CONVERSATION_HISTORY=3
UPLOAD_DIR=data/uploads
MAX_FILE_SIZE_MB=200
PAGE_TITLE=RAG Chatbot Platform
PAGE_LAYOUT=wide
```

## Usage Workflow

1. **Start Application**: `streamlit run app.py`
2. **Upload Documents**: Go to "📄 Upload Documents" → Create knowledge base → Upload PDFs
3. **Select Knowledge Base**: Use sidebar dropdown to select your knowledge base
4. **Start Chatting**: Go to "💬 Chat" → Ask questions about your documents
5. **Manage Knowledge**: Switch between knowledge bases or add more documents

## Key Features Implemented

✅ **Professional ChatGPT-like UI** with streaming responses  
✅ **PDF document processing** with chunking and vector embeddings  
✅ **Knowledge base management** with creation/switching/deletion  
✅ **Conversation memory** maintaining 3-message history  
✅ **RAG implementation** with semantic search and contextual responses  
✅ **Session state management** for chat persistence  
✅ **Modular architecture** separating UI from core logic  
✅ **Error handling** with user-friendly messages  
✅ **Configuration management** via environment variables  
✅ **Unit test coverage** for core components  

## Troubleshooting

### Common Issues

1. **Missing OpenAI API Key**
   - Ensure `.env` file exists with valid `OPENAI_API_KEY`
   - Restart application after updating `.env`

2. **Dependency Errors**
   - Run: `pip install -r requirements.txt`
   - Ensure Python 3.8+ is installed

3. **Vector Database Issues**
   - Check that `data/` directories are writable
   - Clear `data/knowledge_bases/` if corruption occurs

4. **Large PDF Processing Fails**
   - Check available memory
   - Reduce `CHUNK_SIZE` in `.env` if needed
   - Ensure PDF is not password-protected

### Validation Commands

Run these if you encounter issues:

```bash
# Validate project structure
python validate_structure.py

# Test core imports (requires dependencies)
python demo_test.py

# Run unit tests
pytest tests/ -v
```

## Production Deployment

For production deployment, consider:

1. **Security**: Use proper secrets management instead of `.env` files
2. **Scaling**: Deploy with proper WSGI server and load balancing
3. **Monitoring**: Add logging, metrics, and health checks  
4. **Storage**: Use persistent volumes for vector database
5. **API Limits**: Implement rate limiting and usage monitoring

## Success Criteria Achieved

All PRP success criteria have been met:

- ✅ Users can upload and process PDF documents successfully
- ✅ Knowledge base creation and switching works seamlessly  
- ✅ Chat interface provides relevant, contextual responses
- ✅ Conversation memory maintains last 3 message exchanges
- ✅ Response streaming works smoothly without blocking
- ✅ All components handle errors gracefully with user feedback
- ✅ Application architecture supports future frontend migration
- ✅ Document processing completes efficiently

The RAG Chatbot Platform is now ready for use!