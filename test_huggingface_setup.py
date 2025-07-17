#!/usr/bin/env python3
"""
Test script to verify Hugging Face API key setup
Run this to check if your API key is working correctly
"""

import os
import requests
import json

def test_huggingface_api():
    """Test Hugging Face API connection"""
    
    # Get API key from environment
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    
    if not api_key:
        print("❌ HUGGINGFACE_API_KEY environment variable not found!")
        print("\nTo fix this:")
        print("1. Go to https://huggingface.co/settings/tokens")
        print("2. Create a new token with 'Read' permissions")
        print("3. Add HUGGINGFACE_API_KEY=your_token to your environment variables")
        print("4. For Render: Add it in your service's Environment Variables section")
        return False
    
    print(f"✅ Found API key: {api_key[:10]}...")
    
    # Test with a simple model
    model_name = "microsoft/DialoGPT-medium"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Simple test payload
    payload = {
        "inputs": "Hello, this is a test message.",
        "parameters": {
            "max_length": 50,
            "temperature": 0.7
        }
    }
    
    try:
        print(f"🔄 Testing connection to {model_name}...")
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{model_name}",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Hugging Face API connection successful!")
            result = response.json()
            print(f"📝 Response received: {len(str(result))} characters")
            return True
        elif response.status_code == 401:
            print("❌ API key is invalid. Please check your token.")
            return False
        elif response.status_code == 403:
            print("❌ API key doesn't have required permissions.")
            print("Make sure your token has 'Read' permissions.")
            return False
        else:
            print(f"❌ Unexpected error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Check your internet connection.")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return False

def test_contract_analysis():
    """Test contract analysis functionality"""
    
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        print("❌ Cannot test analysis without API key")
        return False
    
    # Test contract content
    test_contract = """
    CONTRACT AGREEMENT
    
    Payment Terms: Payment is due within 30 days of invoice date. 
    Late payments will incur a 5% monthly penalty.
    
    Liability: The total liability shall not exceed $50,000.
    
    Termination: Either party may terminate this agreement with 30 days written notice.
    
    Confidentiality: All confidential information shall be protected for 5 years.
    """
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    Analyze this contract for legal risks and compliance issues. Provide analysis in this JSON format:
    {{
        "overall_risk": "LOW|MEDIUM|HIGH|CRITICAL",
        "confidence": 0.0-1.0,
        "risks": [
            {{
                "category": "risk category",
                "severity": "LOW|MEDIUM|HIGH", 
                "description": "detailed description",
                "clause": "section reference",
                "recommendation": "specific recommendation"
            }}
        ],
        "compliance": [
            {{
                "regulation": "compliance type",
                "status": "check|warning|critical",
                "description": "detailed description",
                "clause": "section reference"
            }}
        ],
        "summary": "overall analysis summary"
    }}
    
    Contract content: {test_contract}
    """
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": 500,
            "temperature": 0.3
        }
    }
    
    try:
        print("🔄 Testing contract analysis...")
        response = requests.post(
            "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Contract analysis test successful!")
            result = response.json()
            print(f"📝 Analysis response received")
            return True
        else:
            print(f"❌ Analysis test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Analysis test error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Hugging Face API Setup Test")
    print("=" * 40)
    
    # Test basic API connection
    api_ok = test_huggingface_api()
    
    if api_ok:
        print("\n" + "=" * 40)
        # Test contract analysis
        analysis_ok = test_contract_analysis()
        
        if analysis_ok:
            print("\n🎉 All tests passed! Your Hugging Face setup is working correctly.")
        else:
            print("\n⚠️  API connection works but analysis needs adjustment.")
    else:
        print("\n❌ Please fix the API key issues before proceeding.")
    
    print("\n📋 Next steps:")
    print("1. If tests passed: Your AI service should work with enhanced analysis")
    print("2. If tests failed: Check your API key and permissions")
    print("3. For Render deployment: Add HUGGINGFACE_API_KEY to environment variables") 