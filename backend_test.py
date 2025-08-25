import requests
import sys
import json
from datetime import datetime

class TestPlatformAPITester:
    def __init__(self, base_url=None):
        if base_url is None:
            # Use environment variable or default for current deployment
            import os
            frontend_url = os.environ.get('REACT_APP_BACKEND_URL', 'https://testify-5.preview.emergentagent.com')
            base_url = f"{frontend_url}/api"
        self.base_url = base_url
        self.admin_token = None
        self.student_token = None
        self.admin_user = None
        self.student_user = None
        self.test_id = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Response text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_basic_connectivity(self):
        """Test basic API connectivity"""
        print("\n" + "="*50)
        print("TESTING BASIC CONNECTIVITY")
        print("="*50)
        
        success, response = self.run_test(
            "Basic API Root",
            "GET",
            "",
            200
        )
        return success

    def test_authentication(self):
        """Test user registration and login"""
        print("\n" + "="*50)
        print("TESTING AUTHENTICATION")
        print("="*50)
        
        # Test admin registration
        timestamp = datetime.now().strftime('%H%M%S')
        admin_data = {
            "email": f"test_admin_{timestamp}@test.com",
            "name": "Test Admin",
            "password": "admin123",
            "role": "admin"
        }
        
        success, response = self.run_test(
            "Admin Registration",
            "POST",
            "register",
            200,
            data=admin_data
        )
        
        if success:
            self.admin_user = response
        
        # Test student registration
        student_data = {
            "email": f"test_student_{timestamp}@test.com",
            "name": "Test Student",
            "password": "student123",
            "role": "student"
        }
        
        success, response = self.run_test(
            "Student Registration",
            "POST",
            "register",
            200,
            data=student_data
        )
        
        if success:
            self.student_user = response
        
        # Test admin login
        admin_login = {
            "email": admin_data["email"],
            "password": admin_data["password"]
        }
        
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "login",
            200,
            data=admin_login
        )
        
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            print(f"   Admin token obtained: {self.admin_token[:20]}...")
        
        # Test student login
        student_login = {
            "email": student_data["email"],
            "password": student_data["password"]
        }
        
        success, response = self.run_test(
            "Student Login",
            "POST",
            "login",
            200,
            data=student_login
        )
        
        if success and 'access_token' in response:
            self.student_token = response['access_token']
            print(f"   Student token obtained: {self.student_token[:20]}...")
        
        # Test demo accounts
        demo_admin_login = {
            "email": "admin@test.com",
            "password": "admin123"
        }
        
        success, response = self.run_test(
            "Demo Admin Login",
            "POST",
            "login",
            200,
            data=demo_admin_login
        )
        
        demo_student_login = {
            "email": "student@test.com",
            "password": "student123"
        }
        
        success, response = self.run_test(
            "Demo Student Login",
            "POST",
            "login",
            200,
            data=demo_student_login
        )
        
        return self.admin_token and self.student_token

    def test_admin_functionality(self):
        """Test admin-specific functionality"""
        print("\n" + "="*50)
        print("TESTING ADMIN FUNCTIONALITY")
        print("="*50)
        
        if not self.admin_token:
            print("❌ No admin token available, skipping admin tests")
            return False
        
        # Test creating a test
        test_data = {
            "title": "Sample Math Test",
            "description": "A basic math test for testing purposes",
            "price": 9.99,
            "duration_minutes": 30,
            "questions": [
                {
                    "question_text": "What is 2 + 2?",
                    "options": ["3", "4", "5", "6"],
                    "correct_answer": 1,
                    "explanation": "2 + 2 equals 4"
                },
                {
                    "question_text": "What is 5 * 3?",
                    "options": ["12", "15", "18", "20"],
                    "correct_answer": 1,
                    "explanation": "5 * 3 equals 15"
                }
            ]
        }
        
        success, response = self.run_test(
            "Create Test",
            "POST",
            "admin/tests",
            200,
            data=test_data,
            token=self.admin_token
        )
        
        if success and 'id' in response:
            self.test_id = response['id']
            print(f"   Test created with ID: {self.test_id}")
        
        # Test getting admin tests
        success, response = self.run_test(
            "Get Admin Tests",
            "GET",
            "admin/tests",
            200,
            token=self.admin_token
        )
        
        # Test getting students
        success, response = self.run_test(
            "Get Students",
            "GET",
            "admin/students",
            200,
            token=self.admin_token
        )
        
        return True

    def test_student_functionality(self):
        """Test student-specific functionality"""
        print("\n" + "="*50)
        print("TESTING STUDENT FUNCTIONALITY")
        print("="*50)
        
        if not self.student_token:
            print("❌ No student token available, skipping student tests")
            return False
        
        # Test getting available tests
        success, response = self.run_test(
            "Get Available Tests",
            "GET",
            "tests",
            200
        )
        
        # Test getting purchased tests (should be empty initially)
        success, response = self.run_test(
            "Get Purchased Tests (Empty)",
            "GET",
            "my-tests",
            200,
            token=self.student_token
        )
        
        # Test getting results (should be empty initially)
        success, response = self.run_test(
            "Get My Results (Empty)",
            "GET",
            "my-results",
            200,
            token=self.student_token
        )
        
        return True

    def test_payment_integration(self):
        """Test Razorpay payment integration"""
        print("\n" + "="*50)
        print("TESTING RAZORPAY PAYMENT INTEGRATION")
        print("="*50)
        
        if not self.student_token or not self.test_id:
            print("❌ No student token or test ID available, skipping payment tests")
            return False
        
        # Test creating payment order
        success, response = self.run_test(
            "Create Payment Order",
            "POST",
            f"tests/{self.test_id}/purchase",
            200,
            token=self.student_token
        )
        
        order_id = None
        if success and 'order_id' in response:
            order_id = response['order_id']
            print(f"   Payment order created: {order_id}")
            print(f"   Amount: {response.get('amount', 'N/A')} paise")
            print(f"   Currency: {response.get('currency', 'N/A')}")
            print(f"   Key ID: {response.get('key_id', 'N/A')}")
            print(f"   Test Title: {response.get('test_title', 'N/A')}")
        
        # Test duplicate purchase prevention
        success, response = self.run_test(
            "Prevent Duplicate Purchase Order",
            "POST",
            f"tests/{self.test_id}/purchase",
            400,  # Should fail with 400 for duplicate
            token=self.student_token
        )
        
        # Test payment verification with invalid signature (should fail)
        if order_id:
            invalid_verification = {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": "pay_test_invalid",
                "razorpay_signature": "invalid_signature"
            }
            
            success, response = self.run_test(
                "Payment Verification (Invalid Signature)",
                "POST",
                "verify-payment",
                400,  # Should fail with invalid signature
                data=invalid_verification,
                token=self.student_token
            )
        
        # Test unauthorized payment verification
        if order_id:
            verification_data = {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": "pay_test_123",
                "razorpay_signature": "test_signature"
            }
            
            success, response = self.run_test(
                "Payment Verification (No Auth)",
                "POST",
                "verify-payment",
                401,  # Should fail without authentication
                data=verification_data
            )
        
        return True

    def test_authorization(self):
        """Test authorization and access control"""
        print("\n" + "="*50)
        print("TESTING AUTHORIZATION")
        print("="*50)
        
        # Test student trying to access admin endpoints
        if self.student_token:
            success, response = self.run_test(
                "Student Access Admin Tests (Should Fail)",
                "GET",
                "admin/tests",
                403,
                token=self.student_token
            )
        
        # Test unauthenticated access
        success, response = self.run_test(
            "Unauthenticated Access (Should Fail)",
            "GET",
            "admin/tests",
            401
        )
        
        return True

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Test Platform API Testing")
        print(f"Base URL: {self.base_url}")
        
        # Run test suites
        self.test_basic_connectivity()
        self.test_authentication()
        self.test_admin_functionality()
        self.test_student_functionality()
        self.test_payment_integration()
        self.test_authorization()
        
        # Print final results
        print("\n" + "="*50)
        print("FINAL RESULTS")
        print("="*50)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print(f"❌ {self.tests_run - self.tests_passed} tests failed")
            return 1

def main():
    tester = TestPlatformAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())