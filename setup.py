"""
Setup script for MFT Finance AI Assistant
"""
import subprocess
import sys
from pathlib import Path

def install_requirements():
    """Install requirements"""
    try:
        print("📦 Installing requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def test_imports():
    """Test if all imports work"""
    try:
        print("🧪 Testing imports...")
        
        # Test core imports
        import torch
        import transformers
        import sentence_transformers
        import chromadb
        import duckdb
        import pandas
        import streamlit
        
        print("✅ All imports successful!")
        
        # Check GPU availability
        if torch.cuda.is_available():
            print(f"🚀 GPU available: {torch.cuda.get_device_name()}")
        else:
            print("💻 Using CPU (consider GPU for better performance)")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def initialize_system():
    """Initialize the system"""
    try:
        print("🚀 Initializing system...")
        from main import FinanceAISystem
        
        system = FinanceAISystem()
        if system.initialize():
            print("✅ System initialized successfully!")
            return True
        else:
            print("❌ System initialization failed!")
            return False
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False

def main():
    """Main setup process"""
    print("🚀 MFT Finance AI Assistant - Setup")
    print("=" * 50)
    
    # Step 1: Install requirements
    if not install_requirements():
        return False
    
    # Step 2: Test imports
    if not test_imports():
        return False
    
    # Step 3: Initialize system
    if not initialize_system():
        return False
    
    print("=" * 50)
    print("🎉 Setup completed successfully!")
    print("")
    print("🚀 To start the application:")
    print("   streamlit run ui.py")
    print("")
    print("💻 For CLI mode:")
    print("   python main.py --interactive")
    
    return True

if __name__ == "__main__":
    main()
