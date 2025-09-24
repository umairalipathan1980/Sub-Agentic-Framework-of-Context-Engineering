#!/usr/bin/env python3
"""
Basic structure validation script for the RAG Chatbot Platform.
Checks that all required files exist and have basic content.
"""

import os
from pathlib import Path

def validate_project_structure():
    """Validate that all required files exist."""
    
    required_files = [
        "app.py",
        "requirements.txt", 
        ".env.example",
        ".streamlit/config.toml",
        
        # Source files
        "src/__init__.py",
        "src/utils/__init__.py",
        "src/utils/config.py",
        "src/core/__init__.py", 
        "src/core/document_processor.py",
        "src/core/vector_store.py",
        "src/core/conversation_manager.py",
        "src/core/rag_engine.py",
        "src/application/__init__.py",
        "src/application/document_upload.py",
        "src/application/chat_interface.py",
        "src/application/streamlit_app.py",
        
        # Test files
        "tests/__init__.py",
        "tests/test_document_processor.py",
        "tests/test_vector_store.py",
        "tests/test_rag_engine.py"
    ]
    
    required_dirs = [
        "data/knowledge_bases",
        "data/uploads",
    ]
    
    print("🔍 Validating project structure...")
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
        else:
            print(f"✅ {dir_path}/")
    
    if missing_files:
        print(f"\n❌ Missing files: {len(missing_files)}")
        for file_path in missing_files:
            print(f"  - {file_path}")
    
    if missing_dirs:
        print(f"\n❌ Missing directories: {len(missing_dirs)}")
        for dir_path in missing_dirs:
            print(f"  - {dir_path}")
    
    if not missing_files and not missing_dirs:
        print("\n🎉 All required files and directories are present!")
        return True
    else:
        print(f"\n⚠️  Found {len(missing_files)} missing files and {len(missing_dirs)} missing directories")
        return False

def validate_file_contents():
    """Basic validation of file contents."""
    print("\n🔍 Validating file contents...")
    
    # Check that key files have expected content
    validations = [
        ("app.py", ["from application.streamlit_app import main", "if __name__ == \"__main__\":"]),
        ("src/utils/config.py", ["class AppConfig", "openai_api_key", "chroma_persist_dir"]),
        ("src/core/document_processor.py", ["class DocumentProcessor", "process_pdf", "RecursiveCharacterTextSplitter"]),
        ("src/core/vector_store.py", ["class VectorStoreManager", "Chroma", "create_knowledge_base"]),
        ("src/core/conversation_manager.py", ["class ConversationManager", "ConversationBufferWindowMemory"]),
        ("src/core/rag_engine.py", ["class RAGEngine", "generate_response", "ChatOpenAI"]),
        ("src/application/streamlit_app.py", ["def main", "st.set_page_config", "RAG Chatbot Platform"]),
        ("requirements.txt", ["streamlit", "langchain", "langchain-chroma", "openai"])
    ]
    
    all_good = True
    for file_path, expected_content in validations:
        if Path(file_path).exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                missing_content = []
                for expected in expected_content:
                    if expected not in content:
                        missing_content.append(expected)
                
                if missing_content:
                    print(f"⚠️  {file_path}: Missing expected content: {missing_content}")
                    all_good = False
                else:
                    print(f"✅ {file_path}: Content validation passed")
            except Exception as e:
                print(f"❌ {file_path}: Error reading file - {e}")
                all_good = False
        else:
            print(f"❌ {file_path}: File not found")
            all_good = False
    
    return all_good

if __name__ == "__main__":
    print("🤖 RAG Chatbot Platform - Structure Validation")
    print("=" * 50)
    
    structure_ok = validate_project_structure()
    content_ok = validate_file_contents()
    
    print("\n" + "=" * 50)
    if structure_ok and content_ok:
        print("🎉 PROJECT VALIDATION PASSED!")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and add your OpenAI API key")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Run the application: streamlit run app.py")
    else:
        print("❌ PROJECT VALIDATION FAILED!")
        print("\nPlease fix the issues above before proceeding.")