#!/usr/bin/env python3
"""
Demo test script for the RAG Chatbot Platform.
Tests core functionality without requiring a full Streamlit session.
"""

import os
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_core_imports():
    """Test that all core modules can be imported."""
    print("🔍 Testing core module imports...")
    
    try:
        from utils.config import AppConfig, get_config, ensure_directories_exist
        print("✅ utils.config imported successfully")
        
        from core.document_processor import DocumentProcessor  
        print("✅ core.document_processor imported successfully")
        
        from core.vector_store import VectorStoreManager
        print("✅ core.vector_store imported successfully")
        
        from core.conversation_manager import ConversationManager
        print("✅ core.conversation_manager imported successfully")
        
        from core.rag_engine import RAGEngine
        print("✅ core.rag_engine imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_config_loading():
    """Test configuration loading with environment variables."""
    print("\n🔍 Testing configuration loading...")
    
    try:
        # Test without OpenAI key (should work but warn)
        from utils.config import AppConfig
        
        # Create minimal config for testing
        os.environ['OPENAI_API_KEY'] = 'test-key-for-demo'
        
        config = AppConfig()
        
        print(f"✅ Config loaded:")
        print(f"  - Model: {config.openai_model}")
        print(f"  - Chunk size: {config.chunk_size}")
        print(f"  - Chunk overlap: {config.chunk_overlap}")
        print(f"  - Max conversation history: {config.max_conversation_history}")
        print(f"  - Chroma persist dir: {config.chroma_persist_dir}")
        print(f"  - Upload dir: {config.upload_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Config loading error: {e}")
        return False

def test_directory_creation():
    """Test directory creation functionality."""
    print("\n🔍 Testing directory creation...")
    
    try:
        from utils.config import get_config, ensure_directories_exist
        
        config = get_config()
        ensure_directories_exist(config)
        
        # Check if directories exist
        chroma_dir = Path(config.chroma_persist_dir)
        upload_dir = Path(config.upload_dir)
        
        if chroma_dir.exists():
            print(f"✅ Chroma directory created: {chroma_dir}")
        else:
            print(f"❌ Chroma directory not found: {chroma_dir}")
            
        if upload_dir.exists():
            print(f"✅ Upload directory created: {upload_dir}")
        else:
            print(f"❌ Upload directory not found: {upload_dir}")
            
        return chroma_dir.exists() and upload_dir.exists()
        
    except Exception as e:
        print(f"❌ Directory creation error: {e}")
        return False

def test_component_instantiation():
    """Test instantiation of core components (without external dependencies)."""
    print("\n🔍 Testing component instantiation...")
    
    try:
        from utils.config import get_config
        from core.document_processor import DocumentProcessor
        from core.conversation_manager import ConversationManager
        
        config = get_config()
        
        # Test document processor
        doc_processor = DocumentProcessor(config)
        print("✅ DocumentProcessor instantiated")
        
        # Test conversation manager  
        conv_manager = ConversationManager(config)
        print("✅ ConversationManager instantiated")
        
        # Test basic conversation manager functionality
        conv_manager.add_user_message("Hello, this is a test message")
        messages = conv_manager.get_session_messages()
        print(f"✅ ConversationManager basic functionality: {len(messages)} messages")
        
        return True
        
    except Exception as e:
        print(f"❌ Component instantiation error: {e}")
        return False

def main():
    """Run all demo tests."""
    print("🤖 RAG Chatbot Platform - Demo Test")
    print("=" * 50)
    
    # Override environment for testing
    os.environ['OPENAI_API_KEY'] = 'test-key-for-demo-only'
    
    tests = [
        ("Core Imports", test_core_imports),
        ("Configuration Loading", test_config_loading), 
        ("Directory Creation", test_directory_creation),
        ("Component Instantiation", test_component_instantiation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'=' * 20} {test_name} {'=' * 20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED" 
        print(f"{status:<12} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 ALL TESTS PASSED!")
        print("\nThe core components are working correctly.")
        print("You can now proceed to test the full application with:")
        print("  1. Set up your .env file with a real OpenAI API key")
        print("  2. Install dependencies: pip install -r requirements.txt") 
        print("  3. Run: streamlit run app.py")
    else:
        print(f"\n⚠️  {len(results) - passed} TESTS FAILED!")
        print("Please fix the issues above before proceeding.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)