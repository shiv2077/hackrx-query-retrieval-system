# main.py
import uvicorn
from app.api import app
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Verify required environment variables
    required_vars = [
        "OPENAI_API_KEY",
        "PINECONE_API_KEY",
        "HACKATHON_BEARER_TOKEN"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"Error: Missing required environment variables: {missing_vars}")
        print("Please check your .env file")
        exit(1)
    
    print("Starting RAG System...")
    print("Make sure your .env file contains all required API keys")
    
    uvicorn.run(
        "app.api:app",  # Use import string instead of app object
        host="0.0.0.0", 
        port=8000,
        reload=True  # This now works with import string
    )