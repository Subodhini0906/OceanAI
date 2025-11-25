"""
Quick start script for FastAPI backend
"""
import uvicorn
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    print("🚀 Starting FastAPI Backend...")
    print("🌐 API will be available at http://localhost:8000")
    print("📚 API docs at http://localhost:8000/docs")
    print("=" * 50)
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

