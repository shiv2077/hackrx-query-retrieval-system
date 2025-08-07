#!/usr/bin/env python3
"""
Test different embedding models available in the hackathon API
"""

from openai import OpenAI

# Use the first working API key
api_key = "sk-5_WepeRibzYS9pJQQajeTg"

client = OpenAI(
    api_key=api_key,
    base_url="https://agent.dev.hyperverge.org"
)

# Different embedding models to try
embedding_models = [
    "text-embedding-3-small",
    "text-embedding-3-large", 
    "text-embedding-ada-002",
    "openai/text-embedding-3-small",
    "openai/text-embedding-3-large",
    "openai/text-embedding-ada-002",
    "embedding"
]

test_text = "This is a test document for embedding"

for model in embedding_models:
    try:
        print(f"Testing embedding model: {model}")
        response = client.embeddings.create(
            model=model,
            input=test_text
        )
        print(f"✅ SUCCESS: {model} - Embedding dimension: {len(response.data[0].embedding)}")
        break
    except Exception as e:
        print(f"❌ FAILED: {model} - {str(e)[:100]}")

print("\nTesting list models endpoint...")
try:
    models = client.models.list()
    print("Available models:")
    for model in models.data:
        print(f"  - {model.id}")
except Exception as e:
    print(f"❌ Could not list models: {e}")
