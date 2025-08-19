#!/usr/bin/env python3

import os
import django
import json
import sys
import requests

# Set up Django environment
sys.path.append('/home/anveg/Development/Tech_assessment/reimagined')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mindtimer.settings')
django.setup()

from dotenv import load_dotenv
from tasks.services import ClaudeTaskGroomer

load_dotenv()

def test_claude_api_direct():
    """Test Claude API directly with various diagnostic checks"""
    print("=== Claude API Diagnostic Test ===")
    
    # Check API key
    api_key = os.getenv('CLAUDE_API_KEY')
    if not api_key:
        print("❌ CLAUDE_API_KEY not found in environment!")
        return False
    
    print(f"✅ API Key found: {api_key[:15]}...")
    print(f"🔍 API Key format check: {'✅ Correct (starts with sk-ant-)' if api_key.startswith('sk-ant-') else '❌ Invalid format'}")
    
    # Test different endpoints to diagnose 404 issue
    base_url = "https://api.anthropic.com"
    endpoints_to_test = [
        "/v1/messages",
        "/v1/complete", 
        "/health",
        "/"
    ]
    
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key,
        'anthropic-version': '2023-06-01'
    }
    
    print("\n🔍 Testing different endpoints...")
    for endpoint in endpoints_to_test:
        url = base_url + endpoint
        try:
            # Try a simple GET first to see what endpoints exist
            response = requests.get(url, headers=headers, timeout=10)
            print(f"GET {endpoint}: {response.status_code} - {response.reason}")
            
            if endpoint == "/v1/messages":
                # Try the actual POST request
                payload = {
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": "Hello"}]
                }
                post_response = requests.post(url, headers=headers, json=payload, timeout=10)
                print(f"POST {endpoint}: {post_response.status_code} - {post_response.reason}")
                
                if post_response.status_code != 200:
                    try:
                        error_details = post_response.json()
                        print(f"    Error details: {json.dumps(error_details, indent=2)}")
                    except:
                        print(f"    Response text: {post_response.text[:200]}...")
                else:
                    print("    ✅ Messages API working!")
                    
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint}: Request failed - {e}")
    
    # Test TaskGroomer with actual groom_tasks function
    print("\n🧪 Testing TaskGroomer.groom_tasks()...")
    try:
        groomer = ClaudeTaskGroomer()
        test_todo = "Do laundry\nBuy groceries"
        test_context = "test context"
        
        print(f"🔍 Calling groomer.groom_tasks('{test_todo}', '{test_context}')")
        result = groomer.groom_tasks(test_todo, test_context)
        
        print("📄 groom_tasks result:")
        print(json.dumps(result, indent=2))
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ TaskGroomer failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_claude_api_direct()
    sys.exit(0 if success else 1)