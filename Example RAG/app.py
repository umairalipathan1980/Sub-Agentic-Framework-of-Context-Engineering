"""
Application entry point for the RAG Chatbot Platform.
Initializes the environment and launches the Streamlit application.
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the main application
if __name__ == "__main__":
    from application.streamlit_app import main
    main()