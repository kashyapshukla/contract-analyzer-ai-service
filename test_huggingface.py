#!/usr/bin/env python3
"""
Test script to verify Hugging Face integration
"""

import asyncio
import os
import requests
from enhanced_analysis import EnhancedContractAnalyzer

async def test_huggingface_integration():
    """Test Hugging Face integration"""
    
    print("🧪 Testing Hugging Face Integration...")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = EnhancedContractAnalyzer()
    
    # Test contract content
    test_content = """
    CONTRACT AGREEMENT
    
    This agreement includes the following terms:
    
    1. LIABILITY: The party shall be liable for damages up to $500,000.
    2. INDEMNIFICATION: Party A shall indemnify Party B for all claims.
    3. PAYMENT TERMS: Payment is due within 30 days with 2% late fee.
    4. TERMINATION: Either party may terminate with 60 days notice.
    5. CONFIDENTIALITY: All information shall remain confidential for 5 years.
    6. GDPR COMPLIANCE: Personal data processing shall comply with GDPR.
    
    This contract contains force majeure clauses and arbitration provisions.
    """
    
    print("📄 Test Contract Content:")
    print(test_content)
    print("\n" + "=" * 50)
    
    # Test 1: Check if Hugging Face API key is configured
    print("🔑 Testing API Key Configuration...")
    if analyzer.huggingface_api_key:
        print("✅ Hugging Face API key is configured")
        print(f"   Key: {analyzer.huggingface_api_key[:10]}...")
    else:
        print("❌ Hugging Face API key is NOT configured")
        print("   Set HUGGINGFACE_API_KEY environment variable")
    
    print("\n" + "=" * 50)
    
    # Test 2: Test Hugging Face API directly
    print("🤖 Testing Hugging Face API Directly...")
    if analyzer.huggingface_api_key:
        try:
            result = await analyzer.analyze_with_huggingface(test_content)
            if result:
                print("✅ Hugging Face API call successful!")
                print(f"   Overall Risk: {result.get('overall_risk', 'N/A')}")
                print(f"   Risks Found: {len(result.get('risks', []))}")
                print(f"   Compliance Issues: {len(result.get('compliance', []))}")
                print(f"   Summary: {result.get('summary', 'N/A')[:100]}...")
            else:
                print("❌ Hugging Face API call failed")
        except Exception as e:
            print(f"❌ Hugging Face API error: {str(e)}")
    else:
        print("⏭️  Skipping API test (no key configured)")
    
    print("\n" + "=" * 50)
    
    # Test 3: Test AI-powered analysis with fallback
    print("🧠 Testing AI-Powered Analysis with Fallback...")
    try:
        risks, risk_score = await analyzer.analyze_risks_with_ai(test_content)
        print("✅ AI analysis completed!")
        print(f"   Risk Score: {risk_score}")
        print(f"   Risks Found: {len(risks)}")
        
        for i, risk in enumerate(risks[:3], 1):  # Show first 3 risks
            print(f"   Risk {i}: {risk['category']} ({risk['severity']})")
            
    except Exception as e:
        print(f"❌ AI analysis error: {str(e)}")
    
    print("\n" + "=" * 50)
    
    # Test 4: Test pattern matching fallback
    print("🔍 Testing Pattern Matching Fallback...")
    try:
        risks, risk_score = analyzer.analyze_risks(test_content)
        print("✅ Pattern matching completed!")
        print(f"   Risk Score: {risk_score}")
        print(f"   Risks Found: {len(risks)}")
        
        for i, risk in enumerate(risks[:3], 1):  # Show first 3 risks
            print(f"   Risk {i}: {risk['category']} ({risk['severity']})")
            
    except Exception as e:
        print(f"❌ Pattern matching error: {str(e)}")
    
    print("\n" + "=" * 50)
    
    # Test 5: Test compliance analysis
    print("📋 Testing Compliance Analysis...")
    try:
        compliance = analyzer.analyze_compliance(test_content)
        print("✅ Compliance analysis completed!")
        print(f"   Compliance Issues: {len(compliance)}")
        
        for i, comp in enumerate(compliance[:3], 1):  # Show first 3 compliance issues
            print(f"   Compliance {i}: {comp['regulation']} ({comp['status']})")
            
    except Exception as e:
        print(f"❌ Compliance analysis error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ Testing Complete!")

def test_api_endpoint():
    """Test the deployed API endpoint"""
    
    print("🌐 Testing Deployed API Endpoint...")
    print("=" * 50)
    
    url = "https://contract-analyzer-ai-service.onrender.com/analyze"
    
    test_data = {
        "content": "This contract includes liability terms up to $100,000 and payment terms of 30 days.",
        "filename": "test_contract.txt"
    }
    
    try:
        response = requests.post(url, json=test_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API endpoint working!")
            print(f"   Analysis ID: {result.get('analysis_id', 'N/A')}")
            print(f"   Risk Level: {result.get('risk_level', 'N/A')}")
            print(f"   Risk Score: {result.get('risk_score', 'N/A')}")
            print(f"   Risks Found: {len(result.get('risks', []))}")
            print(f"   Summary: {result.get('summary', 'N/A')[:100]}...")
        else:
            print(f"❌ API endpoint error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ API endpoint error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Hugging Face Integration Tests...")
    print()
    
    # Test local integration
    asyncio.run(test_huggingface_integration())
    print()
    
    # Test deployed API
    test_api_endpoint() 