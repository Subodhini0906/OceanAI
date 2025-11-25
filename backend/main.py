from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import json
from pathlib import Path

app = FastAPI(title="Autonomous QA Agent API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class DocumentUpload(BaseModel):
    filename: str
    content: str

class TestCaseRequest(BaseModel):
    query: str
    context: Optional[List[str]] = None

class ScriptGenerationRequest(BaseModel):
    test_case: dict
    html_content: str

# In-memory storage (in production, use proper database)
knowledge_base_status = {"built": False, "document_count": 0}
uploaded_documents = {}
html_content = ""

@app.get("/")
async def root():
    return {"message": "Autonomous QA Agent API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/upload/document")
async def upload_document(file: UploadFile = File(...)):
    """Upload a support document"""
    try:
        content = await file.read()
        
        # Store document
        if file.filename:
            uploaded_documents[file.filename] = {
                "content": content.decode('utf-8', errors='ignore'),
                "type": file.content_type or "text/plain"
            }
        
        return {
            "status": "success",
            "filename": file.filename,
            "message": f"Document {file.filename} uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload/html")
async def upload_html(file: UploadFile = File(...)):
    """Upload HTML file"""
    global html_content
    try:
        content = await file.read()
        html_content = content.decode('utf-8', errors='ignore')
        
        return {
            "status": "success",
            "filename": file.filename,
            "message": "HTML file uploaded successfully",
            "size": len(html_content)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload/html-text")
async def upload_html_text(content: dict):
    """Upload HTML as text"""
    global html_content
    try:
        html_content = content.get("html", "")
        return {
            "status": "success",
            "message": "HTML content received",
            "size": len(html_content)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/build-knowledge-base")
async def build_knowledge_base():
    """Trigger knowledge base building"""
    try:
        # This will be handled by the Streamlit app with direct vector DB access
        # This endpoint is for status tracking
        knowledge_base_status["built"] = True
        knowledge_base_status["document_count"] = len(uploaded_documents)
        
        return {
            "status": "success",
            "message": "Knowledge base building initiated",
            "document_count": knowledge_base_status["document_count"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/knowledge-base/status")
async def get_kb_status():
    """Get knowledge base status"""
    return knowledge_base_status

@app.get("/documents")
async def get_documents():
    """Get list of uploaded documents"""
    return {
        "documents": list(uploaded_documents.keys()),
        "count": len(uploaded_documents)
    }

@app.get("/html")
async def get_html():
    """Get uploaded HTML content"""
    return {
        "html": html_content,
        "size": len(html_content)
    }

@app.post("/generate/test-cases")
async def generate_test_cases(request: TestCaseRequest):
    """Generate test cases based on query"""
    # Actual generation happens in Streamlit with direct LLM access
    # This endpoint is for API-based access
    return {
        "status": "success",
        "message": "Test case generation should be done via Streamlit UI",
        "query": request.query
    }

@app.post("/generate/selenium-script")
async def generate_selenium_script(request: ScriptGenerationRequest):
    """Generate Selenium script from test case"""
    # Actual generation happens in Streamlit with direct LLM access
    return {
        "status": "success",
        "message": "Script generation should be done via Streamlit UI",
        "test_case": request.test_case
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

