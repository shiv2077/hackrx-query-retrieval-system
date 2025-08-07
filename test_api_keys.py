#!/usr/bin/env python3
"""
Test script to find working OpenAI API keys for the hackathon
"""

from openai import OpenAI
import os

# List of API keys to test
api_keys = [
    "sk-5_WepeRibzYS9pJQQajeTg",
    "sk-673jt1UcfTSnIkwhFUBjiw",
    "sk-95MakDWNKO1SvmxreLawSA",
    "sk-315veH9QSCUIdXKPeC_eZA",
    "sk-yYS5e8O0x-HU33E_KIP0-A",
    "sk-tS70vF9G6Tuh0V2vq1KuiQ",
    "sk-UHpRLCjZCTNCt_0Bo796dA",
    "sk-yFKq-8cgsAo-qEXa502mrA",
    "sk-VwgaQg-gwA9m5FThL1XesA",
    "sk-aquejIxDfXWhe_-VJxMmbA",
    "sk-Azhet2tBEmDy0nLkHiOqRw",
    "sk-hvYRbmSnGDx1tYD1muQVkA",
    "sk-2sHa4GMe4UPciCzOFwaWvA",
    "sk-cy1EvgKG3kAIjfCsexBAzA",
    "sk-aEip6jH0OAktSWv7fcNkBg",
    "sk-IRZBxV_CDtKHN1pZYr8_sQ",
    "sk-5xjOFi1j09BA54E5z_OW_A",
    "sk-RSP_YH1wDkHHlSLujhZ1DA"
]

def test_api_key(api_key):
    """Test if an API key works with the hackathon endpoint"""
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://agent.dev.hyperverge.org"
        )
        
        # Test with a simple chat completion
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": "Hello, test message"
                }
            ],
            max_tokens=10
        )
        
        print(f"✅ WORKING: {api_key[:20]}...")
        print(f"   Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {api_key[:20]}... - {str(e)[:100]}")
        return False

def test_embedding_api_key(api_key):
    """Test if an API key works for embeddings"""
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://agent.dev.hyperverge.org"
        )
        
        # Test with embedding
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input="test text"
        )
        
        print(f"✅ EMBEDDING WORKING: {api_key[:20]}...")
        return True
        
    except Exception as e:
        print(f"❌ EMBEDDING FAILED: {api_key[:20]}... - {str(e)[:100]}")
        return False

if __name__ == "__main__":
    print("🔍 Testing API keys for chat completions...")
    print("=" * 50)
    
    working_keys = []
    working_embedding_keys = []
    
    for i, key in enumerate(api_keys, 1):
        print(f"\n[{i}/{len(api_keys)}] Testing: {key[:20]}...")
        
        # Test chat completion
        if test_api_key(key):
            working_keys.append(key)
            
            # If chat works, test embedding too
            if test_embedding_api_key(key):
                working_embedding_keys.append(key)
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    print(f"Working chat keys: {len(working_keys)}")
    print(f"Working embedding keys: {len(working_embedding_keys)}")
    
    if working_keys:
        print(f"\n🎉 BEST KEY TO USE: {working_keys[0]}")
        print("Copy this to your .env file!")
    else:
        print("\n😔 No working keys found")
