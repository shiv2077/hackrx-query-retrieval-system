# app/models.py
from pydantic import BaseModel
from typing import List, Optional

class HackathonRequest(BaseModel):
    documents: str  # URL to the document
    questions: List[str]

class HackathonResponse(BaseModel):
    answers: List[str]

class DocumentChunk(BaseModel):
    id: str
    text: str
    metadata: Optional[dict] = None

class QueryResult(BaseModel):
    answer: str
    confidence: float
    source_chunks: List[str]