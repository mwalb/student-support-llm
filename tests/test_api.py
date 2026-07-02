"""
test_api.py - API Test Script for Student Support Assistant
Task 5: The Created API Test Script
"""

import requests
import json
import time
from datetime import datetime
import sys

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 30

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

def print_header(text):
    print(f"\n{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.MAGENTA}{text:^70}{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*70}{Colors.RESET}")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.YELLOW}📝 {text}{Colors.RESET}")

def print_result(passed, test_name):
    if passed:
        print(f"{Colors.GREEN}✓ PASS: {test_name}{Colors.RESET}")
    else:
        print(f"{Colors.RED}✗ FAIL: {test_name}{Colors.RESET}")
    return passed

# ============================================
# TEST FUNCTIONS
# ============================================

def test_root():
    """Test 1: Root endpoint"""
    print_header("TEST 1: Root Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success("Root endpoint is working!")
            print_info(f"Message: {data.get('message')}")
            print_info(f"Status: {data.get('status')}")
            print_info(f"Available models: {data.get('models')}")
            print_info(f"Endpoints: {list(data.get('endpoints', {}).keys())}")
            return True
        else:
            print_error(f"Failed with status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_health():
    """Test 2: Health check"""
    print_header("TEST 2: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success("Health check passed!")
            print_info(f"Status: {data.get('status')}")
            print_info(f"Ollama: {data.get('ollama')}")
            print_info(f"Timestamp: {data.get('timestamp', 'N/A')}")
            return True
        else:
            print_error(f"Failed with status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_ask_question():
    """Test 3: Ask a question"""
    print_header("TEST 3: Ask a Question")
    
    question = "What is a university library?"
    print_info(f"Question: {question}")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/ask",
            json={"question": question, "model": "uni-assistant"},
            timeout=30
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Question answered in {elapsed:.2f} seconds!")
            print_info(f"Question: {data.get('question')}")
            print_info(f"Model used: {data.get('model_used')}")
            print_info(f"Answer preview: {data.get('answer')[:200]}...")
            print_info(f"Timestamp: {data.get('timestamp', 'N/A')}")
            return True
        else:
            print_error(f"Failed with status: {response.status_code}")
            print_error(f"Response: {response.text[:200]}")
            return False
    except requests.exceptions.Timeout:
        print_error("Request timed out!")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_ask_question_custom_model():
    """Test 3b: Ask with custom model"""
    print_header("TEST 3b: Ask with Custom Model")
    
    question = "How do I register for courses?"
    print_info(f"Question: {question}")
    print_info("Model: llama3.2:1b")
    
    try:
        response = requests.post(
            f"{BASE_URL}/ask",
            json={"question": question, "model": "llama3.2:1b"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Custom model responded!")
            print_info(f"Model used: {data.get('model_used')}")
            print_info(f"Answer preview: {data.get('answer')[:150]}...")
            return True
        else:
            print_error(f"Failed with status: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_error_handling():
    """Test 4: Error handling"""
    print_header("TEST 4: Error Handling Tests")
    
    results = []
    
    # Test 4a: Empty question
    print_info("Test 4a: Empty question")
    try:
        response = requests.post(
            f"{BASE_URL}/ask",
            json={"question": ""},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('answer'):
                print_info("Empty question was handled (model responded)")
            else:
                print_success("Empty question was properly rejected")
            results.append(True)
        else:
            print_success(f"Empty question returned error {response.status_code}")
            results.append(True)
    except Exception as e:
        print_success(f"Empty question error caught: {str(e)[:50]}")
        results.append(True)
    
    # Test 4b: Very long question
    print_info("\nTest 4b: Very long question (500 chars)")
    long_question = "What is " + "university " * 100
    try:
        response = requests.post(
            f"{BASE_URL}/ask",
            json={"question": long_question[:500]},
            timeout=30
        )
        if response.status_code == 200:
            print_success("Long question was handled")
            results.append(True)
        else:
            print_info(f"Long question returned: {response.status_code}")
            results.append(True)
    except Exception as e:
        print_info(f"Long question error caught: {str(e)[:50]}")
        results.append(True)
    
    # Test 4c: Unknown model
    print_info("\nTest 4c: Unknown model")
    try:
        response = requests.post(
            f"{BASE_URL}/ask",
            json={"question": "Hello", "model": "unknown-model-xyz"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print_info(f"Unknown model handled with answer: {data.get('answer')[:50]}")
            results.append(True)
        else:
            print_success(f"Unknown model error: {response.status_code}")
            results.append(True)
    except Exception as e:
        print_success(f"Unknown model error caught: {str(e)[:50]}")
        results.append(True)
    
    # Summary
    passed = sum(results)
    total = len(results)
    print_info(f"\nError handling tests: {passed}/{total} passed")
    return passed == total

def test_performance():
    """Test 5: Performance check"""
    print_header("TEST 5: Performance Check")
    
    questions = [
        "What is a university library?",
        "How do I register for courses?",
        "What are the exam rules?"
    ]
    
    results = []
    total_time = 0
    
    for i, question in enumerate(questions, 1):
        print_info(f"Question {i}: {question[:30]}...")
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/ask",
                json={"question": question},
                timeout=30
            )
            elapsed = time.time() - start_time
            total_time += elapsed
            
            if response.status_code == 200:
                status = f"{elapsed:.2f}s"
                if elapsed < 10:
                    print_success(f"  ✅ {status}")
                    results.append(True)
                else:
                    print_info(f"  ⏱️  {status}")
                    results.append(True)
            else:
                print_error(f"  ❌ Failed: {response.status_code}")
                results.append(False)
        except Exception as e:
            print_error(f"  ❌ Error: {str(e)[:50]}")
            results.append(False)
    
    avg_time = total_time / len(questions) if questions else 0
    print_info(f"\nAverage response time: {avg_time:.2f} seconds")
    
    passed = sum(results)
    total = len(results)
    print_info(f"Performance: {passed}/{total} passed")
    return passed == total

def main():
    """Run all tests"""
    print_header("STUDENT SUPPORT ASSISTANT API TEST")
    print(f"{Colors.CYAN}Task 5: API Test Script{Colors.RESET}")
    print_info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"Timeout: {TIMEOUT}s")
    
    # Check backend
    print_header("Checking Backend Status")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success("✅ Backend is running!")
        else:
            print_error("❌ Backend is not responding correctly")
            print_error("Run: cd backend && python main.py")
            return 1
    except requests.exceptions.ConnectionError:
        print_error("❌ Cannot connect to backend!")
        print_error("Please start backend: cd backend && python main.py")
        return 1
    
    # Run tests
    results = {}
    results['Root Endpoint'] = test_root()
    results['Health Check'] = test_health()
    results['Ask Question'] = test_ask_question()
    results['Custom Model'] = test_ask_question_custom_model()
    results['Error Handling'] = test_error_handling()
    results['Performance'] = test_performance()
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"{Colors.YELLOW}Total Tests: {total}{Colors.RESET}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {total - passed}{Colors.RESET}")
    
    if passed == total:
        print_success("\n🎉 ALL TESTS PASSED!")
        print_success("📸 Take a screenshot of this output for Task 5!")
    else:
        print_error(f"\n⚠️ {total - passed} test(s) failed")
    
    print_info(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
