#!/usr/bin/env python3
"""
API Health Check - Verify Google AI Studio API is working
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
for env_path in [".env", "experiments/.env", "experiments/batch_run/.env"]:
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)
        print(f"✅ Loaded environment from: {env_path}")

def check_api():
    """Verify Google AI Studio API is accessible"""
    
    # 1. Check API Key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment!")
        print("\nTo fix:")
        print("1. Create .env file in project root or experiments/ folder")
        print("2. Add: GOOGLE_API_KEY=your_api_key_here")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    # 2. Test API Connection
    try:
        import google.generativeai as genai
        print("✅ google-generativeai library installed")
    except ImportError:
        print("❌ google-generativeai not installed!")
        print("\nTo fix: pip install google-generativeai")
        return False
    
    # 3. Configure and test
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        print("🔄 Testing API with simple request...")
        response = model.generate_content('Reply with just "OK" if you are working')
        
        print(f"✅ API Response: {response.text.strip()}")
        print("\n" + "="*60)
        print("🎉 API IS WORKING! Ready for full benchmark.")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"❌ API Test failed: {str(e)}")
        print("\nPossible issues:")
        print("- Invalid API key")
        print("- Network connectivity")
        print("- API quota exceeded")
        print("- Model not accessible")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Google AI Studio API Health Check")
    print("="*60 + "\n")
    
    success = check_api()
    sys.exit(0 if success else 1)
