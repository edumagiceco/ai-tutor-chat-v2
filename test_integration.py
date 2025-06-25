#!/usr/bin/env python3
"""
AI Tutor System Integration Test Script
"""

import requests
import json
import time
from datetime import datetime

# Base URLs
BASE_URL = "http://localhost:8081"
API_URL = f"{BASE_URL}/api/v1"

# Test accounts
TEST_ACCOUNTS = {
    "user": {"email": "user@ai-tutor.com", "password": "user123!"},
    "institution": {"email": "institution@ai-tutor.com", "password": "inst123!"},
    "admin": {"email": "admin@ai-tutor.com", "password": "admin123!@#"}
}

# Test results
results = []

def log_result(test_name, status, message=""):
    """Log test result"""
    result = {
        "test": test_name,
        "status": "✅ PASS" if status else "❌ FAIL",
        "message": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    results.append(result)
    print(f"{result['status']} {test_name}: {message}")

def test_login(account_type):
    """Test login functionality"""
    account = TEST_ACCOUNTS[account_type]
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            data={
                "username": account["email"],
                "password": account["password"]
            }
        )
        if response.status_code == 200:
            data = response.json()
            log_result(f"Login {account_type}", True, "Token received")
            return data["access_token"]
        else:
            log_result(f"Login {account_type}", False, f"Status: {response.status_code}")
            return None
    except Exception as e:
        log_result(f"Login {account_type}", False, str(e))
        return None

def test_user_profile(token):
    """Test user profile API"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            user = response.json()
            log_result("Get user profile", True, f"User: {user['email']}")
            return True
        else:
            log_result("Get user profile", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        log_result("Get user profile", False, str(e))
        return False

def test_create_conversation(token):
    """Test creating a new conversation"""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.post(
            f"{API_URL}/chat/conversations",
            headers=headers,
            json={"title": "Test Conversation"}
        )
        if response.status_code == 200:
            conv = response.json()
            log_result("Create conversation", True, f"ID: {conv['id']}")
            return conv["id"]
        else:
            log_result("Create conversation", False, f"Status: {response.status_code}")
            return None
    except Exception as e:
        log_result("Create conversation", False, str(e))
        return None

def test_send_message(token, conversation_id):
    """Test sending a message"""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.post(
            f"{API_URL}/chat/conversations/{conversation_id}/messages",
            headers=headers,
            json={"content": "AI 도구를 사용해서 업무 효율을 높이는 방법을 알려주세요."}
        )
        if response.status_code == 200:
            log_result("Send message", True, "Message sent and response received")
            return True
        else:
            log_result("Send message", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        log_result("Send message", False, str(e))
        return False

def test_admin_users_list(token):
    """Test admin users list API"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/admin/users", headers=headers)
        if response.status_code == 200:
            users = response.json()
            log_result("Admin users list", True, f"Found {len(users)} users")
            return True
        else:
            log_result("Admin users list", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        log_result("Admin users list", False, str(e))
        return False

def test_admin_access_control():
    """Test access control for different roles"""
    # Test user trying to access admin endpoint
    user_token = test_login("user")
    if user_token:
        headers = {"Authorization": f"Bearer {user_token}"}
        response = requests.get(f"{API_URL}/admin/users", headers=headers)
        if response.status_code == 403:
            log_result("Access control - User blocked from admin", True, "Correctly blocked")
        else:
            log_result("Access control - User blocked from admin", False, f"Status: {response.status_code}")

def run_integration_tests():
    """Run all integration tests"""
    print("\n🧪 AI Tutor System Integration Tests")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backend URL: {BASE_URL}")
    print("=" * 50 + "\n")

    # Test 1: Authentication
    print("📋 Testing Authentication...")
    user_token = test_login("user")
    admin_token = test_login("admin")
    institution_token = test_login("institution")
    
    # Test 2: User Profile
    if user_token:
        print("\n📋 Testing User Profile...")
        test_user_profile(user_token)
    
    # Test 3: Chat Functionality
    if user_token:
        print("\n📋 Testing Chat Functionality...")
        conv_id = test_create_conversation(user_token)
        if conv_id:
            test_send_message(user_token, conv_id)
    
    # Test 4: Admin Features
    if admin_token:
        print("\n📋 Testing Admin Features...")
        test_admin_users_list(admin_token)
    
    # Test 5: Access Control
    print("\n📋 Testing Access Control...")
    test_admin_access_control()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = sum(1 for r in results if "PASS" in r["status"])
    failed = sum(1 for r in results if "FAIL" in r["status"])
    
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(results)*100):.1f}%")
    
    # Save results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\n✅ Results saved to test_results.json")

if __name__ == "__main__":
    run_integration_tests()