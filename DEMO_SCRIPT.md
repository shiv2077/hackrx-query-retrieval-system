# 🎥 Demo Video Script - HackRx Submission

## **Opening (30 seconds)**
"Hi! I'm demonstrating my LLM-Powered Query-Retrieval System for HackRx. This system intelligently processes insurance documents and answers complex queries with detailed, contextual responses."

## **Demo Flow (90 seconds)**

### **1. Show the Live System**
- Navigate to terminal, show server running: `python main.py`
- Show the API endpoint: `http://localhost:8000/hackrx/run`

### **2. Execute Live Demo**
```bash
curl -X POST http://localhost:8000/hackrx/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 971f5fd97a9aff1e0b94e410e77138f521d653ca4d78ddbb1f76c5aa785147a4" \
  -d '{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf",
    "questions": [
        "Does this policy cover maternity expenses?",
        "What are the waiting periods?"
    ]
  }'
```

### **3. Highlight Key Features**
- "Notice the detailed response with specific conditions and age restrictions"
- "The system processes 141 document chunks and uses intelligent semantic search"
- "When standard embeddings aren't available, it falls back to LLM-powered analysis"

## **Technical Highlights (30 seconds)**
- "Built with FastAPI, Pinecone vector database, and GPT-4o-mini"
- "Features intelligent fallback embeddings for production reliability"
- "Optimized for accuracy, token efficiency, and explainability"

## **Closing (30 seconds)**
- "This system is production-ready and already successfully processing real insurance documents"
- "GitHub repository: github.com/shiv2077/hackrx-query-retrieval-system"
- "Thank you for watching!"

---

## **Demo Tips:**
1. **Record your screen** showing the terminal and curl command
2. **Show the JSON response** highlighting the detailed answers
3. **Mention the 141 chunks processed** from the hackathon PDF
4. **Emphasize the intelligent fallback strategy**
5. **Keep it under 3 minutes** - judges have limited time
