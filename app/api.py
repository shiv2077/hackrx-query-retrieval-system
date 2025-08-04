# app/api.py
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from .models import HackathonRequest, HackathonResponse
from .core import RAGSystem

# Load environment variables first
load_dotenv()

app = FastAPI(
    title="LLM-Powered Query-Retrieval System",
    description="RAG system for insurance, legal, HR, and compliance domains",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize RAG system - this will now work since .env is loaded
rag_system = RAGSystem()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify the bearer token"""
    expected_token = os.getenv("HACKATHON_BEARER_TOKEN")
    if credentials.credentials != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return credentials.credentials

@app.get("/")
async def root():
    return {"message": "LLM-Powered Query-Retrieval System is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "rag-system"}

@app.post("/hackrx/run", response_model=HackathonResponse)
async def run_hackrx(
    request: HackathonRequest,
    token: str = Depends(verify_token)
):
    """
    Main endpoint to process documents and answer questions
    """
    try:
        # Validate input
        if not request.documents:
            raise HTTPException(
                status_code=400,
                detail="Document URL is required"
            )
        
        if not request.questions:
            raise HTTPException(
                status_code=400,
                detail="At least one question is required"
            )
        
        # Process questions
        answers = rag_system.process_questions(
            document_url=request.documents,
            questions=request.questions
        )
        
        return HackathonResponse(answers=answers)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/api/v1/status")
async def get_status(token: str = Depends(verify_token)):
    """Get system status"""
    return {
        "status": "operational",
        "processed_documents": len(rag_system.processed_documents),
        "index_name": rag_system.index_name
    }