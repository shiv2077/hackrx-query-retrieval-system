# app/core.py
import os
import openai
from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Any
from .utils import download_pdf, extract_text_from_pdf, create_document_id, chunk_text, clean_text
from .models import DocumentChunk, QueryResult
import time

class RAGSystem:
    def __init__(self):
        # Initialize OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        
        self.index_name = "hackathon-rag-index"
        self.embedding_model = "text-embedding-3-small"
        self.embedding_dimension = 1536
        
        # Create or connect to index
        self._setup_pinecone_index()
        
        # Document cache to avoid reprocessing
        self.processed_documents = {}
    
    def _setup_pinecone_index(self):
        """Setup Pinecone index"""
        try:
            # Check if index exists
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.embedding_dimension,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
                # Wait for index to be ready
                time.sleep(10)
            
            self.index = self.pc.Index(self.index_name)
        except Exception as e:
            print(f"Error setting up Pinecone: {e}")
            raise
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI"""
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return []
    
    def process_document(self, document_url: str) -> bool:
        """Process and index a document"""
        doc_id = create_document_id(document_url)
        
        # Check if already processed
        if doc_id in self.processed_documents:
            print(f"Document {doc_id} already processed, skipping...")
            return True
        
        try:
            # Download and extract text
            print("Downloading document...")
            pdf_bytes = download_pdf(document_url)
            if not pdf_bytes:
                return False
            
            print("Extracting text...")
            text = extract_text_from_pdf(pdf_bytes)
            if not text:
                return False
            
            text = clean_text(text)
            
            # Create chunks
            print("Creating chunks...")
            chunks = chunk_text(text, chunk_size=1000, overlap=200)
            print(f"Created {len(chunks)} chunks")
            
            # Generate embeddings and index
            print("Generating embeddings and indexing...")
            vectors_to_upsert = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_chunk_{i}"
                embedding = self.get_embedding(chunk)
                
                if embedding:
                    vectors_to_upsert.append({
                        'id': chunk_id,
                        'values': embedding,
                        'metadata': {
                            'text': chunk,
                            'doc_id': doc_id,
                            'chunk_index': i,
                            'document_url': document_url
                        }
                    })
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(vectors_to_upsert), batch_size):
                batch = vectors_to_upsert[i:i + batch_size]
                self.index.upsert(vectors=batch)
            
            # Mark as processed
            self.processed_documents[doc_id] = {
                'url': document_url,
                'chunks_count': len(chunks),
                'processed_at': time.time()
            }
            
            print(f"Successfully indexed {len(chunks)} chunks for document {doc_id}")
            return True
            
        except Exception as e:
            print(f"Error processing document: {e}")
            return False
    
    def query_document(self, question: str, top_k: int = 5) -> QueryResult:
        """Query the indexed document"""
        try:
            # Get embedding for question
            question_embedding = self.get_embedding(question)
            if not question_embedding:
                return QueryResult(
                    answer="Error: Could not process question",
                    confidence=0.0,
                    source_chunks=[]
                )
            
            # Search in Pinecone
            search_results = self.index.query(
                vector=question_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            if not search_results.matches:
                return QueryResult(
                    answer="No relevant information found in the document.",
                    confidence=0.0,
                    source_chunks=[]
                )
            
            # Extract context from search results
            context_chunks = []
            source_chunks = []
            
            for match in search_results.matches:
                if match.metadata and 'text' in match.metadata:
                    context_chunks.append(match.metadata['text'])
                    source_chunks.append(f"Relevance: {match.score:.3f} - {match.metadata['text'][:200]}...")
            
            # Generate answer using GPT-4
            answer = self._generate_answer(question, context_chunks)
            
            # Calculate confidence based on top match score
            confidence = search_results.matches[0].score if search_results.matches else 0.0
            
            return QueryResult(
                answer=answer,
                confidence=confidence,
                source_chunks=source_chunks
            )
            
        except Exception as e:
            print(f"Error querying document: {e}")
            return QueryResult(
                answer=f"Error processing query: {str(e)}",
                confidence=0.0,
                source_chunks=[]
            )
    
    def _generate_answer(self, question: str, context_chunks: List[str]) -> str:
        """Generate answer using GPT-4"""
        try:
            # Prepare context
            context = "\n---\n".join(context_chunks)
            
            # Create prompt
            system_prompt = """You are a helpful AI assistant specializing in policy and legal document analysis. 
            You answer questions based ONLY on the provided context from the document. 
            
            Instructions:
            1. If the answer is clearly in the context, provide a detailed and accurate response
            2. If the answer is not in the context, state "The information is not available in the provided document"
            3. Be specific and cite relevant details from the context
            4. Do not make assumptions or add information not present in the context
            5. Maintain a professional and helpful tone"""
            
            user_prompt = f"""Context from document:
---
{context}
---

Question: {question}

Answer:"""
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating answer: {e}")
            return f"Error generating answer: {str(e)}"
    
    def process_questions(self, document_url: str, questions: List[str]) -> List[str]:
        """Process a document and answer multiple questions"""
        # Process document first
        if not self.process_document(document_url):
            return ["Error: Could not process document"] * len(questions)
        
        # Answer each question
        answers = []
        for question in questions:
            result = self.query_document(question)
            answers.append(result.answer)
        
        return answers