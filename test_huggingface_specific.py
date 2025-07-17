#!/usr/bin/env python3
"""
Specific test to check if Hugging Face API is working
"""

import os
import requests
import json

def check_huggingface_api_key():
    """Check if Hugging Face API key is configured"""
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    
    if not api_key:
        print("❌ HUGGINGFACE_API_KEY not found in environment variables")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    return True

def test_huggingface_connection():
    """Test basic Hugging Face API connection"""
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test with a reliable model
    model_name = "gpt2"
    
    payload = {
        "inputs": "Hello, this is a test.",
        "parameters": {
            "max_length": 20,
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
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Hugging Face API connection successful!")
            result = response.json()
            print(f"📝 Response: {result}")
            return True
        elif response.status_code == 401:
            print("❌ 401 Unauthorized - API key is invalid")
            return False
        elif response.status_code == 403:
            print("❌ 403 Forbidden - API key doesn't have required permissions")
            return False
        else:
            print(f"❌ Unexpected error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return False

def test_contract_analysis_specific():
    """Test the exact contract analysis used in the AI service"""
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test contract content (same as in the AI service)
    test_contract = """
    CONTRACT AGREEMENT
    
    Payment Terms: Payment is due within 30 days of invoice date. 
    Late payments will incur a 5% monthly penalty.
    
    Liability: The total liability shall not exceed $50,000.
    
    Termination: Either party may terminate this agreement with 30 days written notice.
    
    Confidentiality: All confidential information shall be protected for 5 years.
    """
    
    prompt = f"""
    Analyze this contract for legal risks and compliance issues. Provide analysis in this JSON format:
    {{
        "overall_risk": "LOW|MEDIUM|HIGH|CRITICAL",
        "confidence": 0.0-1.0,
        "risks": [
            {{
                "category": "risk category",
                "severity": "LOW|MEDIUM|HIGH|CRITICAL", 
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
    
    Focus on: liability, indemnification, termination, confidentiality, force majeure, arbitration, GDPR, SOX, HIPAA compliance.
    """
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": 1000,
            "temperature": 0.3,
            "do_sample": True
        }
    }
    
    try:
        print("🔄 Testing contract analysis with Hugging Face...")
        response = requests.post(
            "https://api-inference.huggingface.co/models/gpt2",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"📊 Analysis Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Contract analysis with Hugging Face successful!")
            result = response.json()
            print(f"📝 Analysis Response: {result}")
            return True
        elif response.status_code == 401:
            print("❌ 401 Unauthorized - API key is invalid for analysis")
            return False
        elif response.status_code == 403:
            print("❌ 403 Forbidden - API key doesn't have required permissions for analysis")
            return False
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Analysis test error: {str(e)}")
        return False

def test_deployed_service():
    """Test the deployed AI service endpoint"""
    try:
        print("🔄 Testing deployed AI service...")
        
        test_data = {
            "content": "Payment due in 30 days with 5% late fees. Total liability limited to $50,000.",
            "filename": "test-contract.txt"
        }
        
        response = requests.post(
            "https://contract-analyzer-ai-service.onrender.com/analyze",
            json=test_data,
            timeout=30
        )
        
        print(f"📊 Deployed Service Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Deployed service is working!")
            print(f"📝 Risk Level: {result.get('risk_level', 'N/A')}")
            print(f"📝 Risk Score: {result.get('risk_score', 'N/A')}")
            print(f"📝 Risks Found: {len(result.get('risks', []))}")
            print(f"📝 Compliance Issues: {len(result.get('compliance', []))}")
            return True
        else:
            print(f"❌ Deployed service error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Deployed service test error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 Hugging Face Specific Test")
    print("=" * 50)
    
    # Test 1: Check API key
    print("\n1. Checking API Key...")
    api_key_ok = check_huggingface_api_key()
    
    if not api_key_ok:
        print("\n❌ Cannot proceed without API key")
        print("Please add HUGGINGFACE_API_KEY to your environment variables")
        exit(1)
    
    # Test 2: Basic connection
    print("\n2. Testing Basic Connection...")
    connection_ok = test_huggingface_connection()
    
    # Test 3: Contract analysis
    print("\n3. Testing Contract Analysis...")
    analysis_ok = test_contract_analysis_specific()
    
    # Test 4: Deployed service
    print("\n4. Testing Deployed Service...")
    deployed_ok = test_deployed_service()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY:")
    print(f"API Key: {'✅' if api_key_ok else '❌'}")
    print(f"Basic Connection: {'✅' if connection_ok else '❌'}")
    print(f"Contract Analysis: {'✅' if analysis_ok else '❌'}")
    print(f"Deployed Service: {'✅' if deployed_ok else '❌'}")
    
    if connection_ok and analysis_ok:
        print("\n🎉 Hugging Face is working correctly!")
        print("Your enhanced AI analysis should be functional.")
    elif connection_ok and not analysis_ok:
        print("\n⚠️  Basic connection works but analysis needs adjustment.")
    else:
        print("\n❌ Hugging Face is not working properly.")
        print("Check your API key and permissions.") 