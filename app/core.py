# app/core.py
import os
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Any
from .utils import download_pdf, extract_text_from_pdf, create_document_id, chunk_text, clean_text
from .models import DocumentChunk, QueryResult
import time

class RAGSystem:
    def __init__(self):
        # Initialize OpenAI client with hackathon endpoint
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://agent.dev.hyperverge.org"
        )
        
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
        """Get embedding for text with fallback strategy"""
        try:
            # First try OpenAI embeddings
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            # Fallback: Use LLM to generate semantic hash
            return self._generate_semantic_embedding(text)
    
    def _generate_semantic_embedding(self, text: str) -> List[float]:
        """Generate semantic embedding using LLM analysis as fallback"""
        try:
            # Use the LLM to extract key semantic features
            response = self.client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "Extract 10 key semantic concepts from the text. Return only comma-separated single words representing the main concepts, topics, and entities."
                    },
                    {
                        "role": "user", 
                        "content": f"Text: {text[:500]}..."  # Limit text length
                    }
                ],
                max_tokens=50
            )
            
            concepts = response.choices[0].message.content.strip().split(',')
            concepts = [c.strip().lower() for c in concepts if c.strip()]
            
            # Convert concepts to numerical embedding (1536 dimensions)
            import hashlib
            import struct
            
            # Create a 1536-dimensional vector
            embedding = [0.0] * 1536
            
            # Use concept hashes to populate the embedding
            for i, concept in enumerate(concepts[:10]):  # Use first 10 concepts
                hash_obj = hashlib.md5(concept.encode())
                hash_bytes = hash_obj.digest()
                
                # Convert hash to multiple float values
                for j in range(0, len(hash_bytes), 4):
                    if j + 4 <= len(hash_bytes):
                        chunk = hash_bytes[j:j+4]
                        if len(chunk) == 4:
                            value = struct.unpack('>f', chunk)[0] if len(chunk) == 4 else 0.0
                            # Normalize to [-1, 1] range
                            value = max(-1.0, min(1.0, value / 1e6))
                            pos = (i * 153 + (j // 4)) % 1536
                            embedding[pos] = value
            
            # Add text length and character distribution features
            text_features = [
                len(text) / 1000.0,  # Normalized length
                text.count(' ') / len(text) if text else 0,  # Word density
                sum(1 for c in text if c.isupper()) / len(text) if text else 0,  # Uppercase ratio
                sum(1 for c in text if c.isdigit()) / len(text) if text else 0,  # Digit ratio
            ]
            
            # Incorporate text features
            for i, feature in enumerate(text_features):
                if i < len(embedding):
                    embedding[i] = (embedding[i] + feature) / 2
            
            return embedding
            
        except Exception as e:
            print(f"Error generating semantic embedding: {e}")
            # Ultimate fallback: simple hash-based embedding
            return self._simple_hash_embedding(text)
    
    def _simple_hash_embedding(self, text: str) -> List[float]:
        """Simple hash-based embedding as ultimate fallback"""
        import hashlib
        import struct
        
        # Create hash of text
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to 1536-dimensional vector
        embedding = []
        for i in range(0, min(len(hash_bytes), 1536 * 4), 4):
            chunk = hash_bytes[i:i+4]
            if len(chunk) == 4:
                value = struct.unpack('>I', chunk)[0] / 4294967295.0  # Normalize to [0,1]
                embedding.append(value * 2 - 1)  # Convert to [-1,1]
            else:
                embedding.append(0.0)
        
        # Pad to 1536 dimensions
        while len(embedding) < 1536:
            embedding.append(0.0)
            
        return embedding[:1536]
    
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
                model="openai/gpt-4o-mini",
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