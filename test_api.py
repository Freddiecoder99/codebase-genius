#!/usr/bin/env python3
"""
Test script for Codebase Genius API
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "admin123"

def get_auth_token():
    """Get authentication token"""
    print("🔐 Getting authentication token...")
    response = requests.post(
        f"{API_BASE}/user/login",
        json={
            "username": USERNAME,
            "password": PASSWORD
        }
    )
    
    if response.status_code == 200:
        token = response.json().get('token')
        print(f"✅ Token obtained: {token[:20]}...")
        return token
    else:
        print(f"❌ Failed to get token: {response.status_code}")
        print(response.text)
        return None

def test_generate_docs(repo_url, token):
    """Test documentation generation"""
    print(f"\n🚀 Generating documentation for: {repo_url}")
    
    response = requests.post(
        f"{API_BASE}/walker/DocumentRepositoryAPI",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "repo_url": repo_url,
            "max_files": 30
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Response received")
        print(f"📋 Full response:")
        print(json.dumps(result, indent=2))
        
        # Check if there are reports
        reports = result.get('reports', [])
        if reports:
            for report in reports:
                if report.get('success'):
                    print(f"\n✅ Success: {report.get('message', 'Documentation generated')}")
                    stats = report.get('statistics', {})
                    print(f"📊 Statistics:")
                    print(f"  - Functions: {stats.get('functions', 0)}")
                    print(f"  - Classes: {stats.get('classes', 0)}")
                    print(f"  - Files analyzed: {stats.get('files_analyzed', 0)}")
                    print(f"📄 Documentation: {report.get('documentation_path')}")
                else:
                    print(f"\n❌ Error: {report.get('error')}")
        return result
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return None

def test_list_docs(token):
    """Test listing documentations"""
    print("\n📚 Listing all documentations...")
    
    response = requests.post(
        f"{API_BASE}/walker/ListDocumentationsAPI",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"📋 Full response:")
        print(json.dumps(result, indent=2))
        
        reports = result.get('reports', [])
        if reports:
            for report in reports:
                if report.get('success'):
                    docs = report.get('documentations', [])
                    print(f"\n✅ Found {report.get('count', 0)} documentation(s):")
                    for doc in docs:
                        print(f"  - {doc['repo_name']} ({doc['size']} bytes)")
        return result
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return None

def test_get_doc(repo_name, token):
    """Test retrieving documentation"""
    print(f"\n📖 Retrieving documentation for: {repo_name}")
    
    response = requests.post(
        f"{API_BASE}/walker/GetDocumentationAPI",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={"repo_name": repo_name}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"📋 Full response:")
        print(json.dumps(result, indent=2)[:500] + "...")
        
        reports = result.get('reports', [])
        if reports:
            for report in reports:
                if report.get('success'):
                    doc = report.get('documentation', '')
                    print(f"\n✅ Retrieved {len(doc)} characters")
                    print(f"\nFirst 200 characters:")
                    print("-" * 50)
                    print(doc[:200])
                    print("-" * 50)
                else:
                    print(f"\n❌ Error: {report.get('error')}")
        return result
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("CODEBASE GENIUS API TEST SUITE")
    print("=" * 60)
    
    # Get authentication token
    token = get_auth_token()
    
    if not token:
        print("\n❌ Failed to authenticate. Exiting.")
        exit(1)
    
    print("\n" + "=" * 60)
    
    # Test 1: Generate documentation
    test_generate_docs("https://github.com/octocat/Hello-World", token)
    
    time.sleep(2)
    
    # Test 2: List all documentations
    test_list_docs(token)
    
    time.sleep(1)
    
    # Test 3: Get specific documentation
    test_get_doc("Hello-World", token)
    
    print("\n" + "=" * 60)
    print("✅ All tests complete!")
    print("=" * 60)
