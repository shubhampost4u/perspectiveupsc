import requests
import sys
import json
from datetime import datetime

class TestPlatformAPITester:
    def __init__(self, base_url=None):
        if base_url is None:
            # Use environment variable or default for current deployment
            import os
            frontend_url = os.environ.get('REACT_APP_BACKEND_URL', 'https://upscpractice.preview.emergentagent.com')
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
        
        # Test existing admin login
        admin_login = {
            "email": "perspectiveupsc1@gmail.com",
            "password": "perspective@2025"
        }
        
        success, response = self.run_test(
            "Existing Admin Login",
            "POST",
            "login",
            200,
            data=admin_login
        )
        
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            self.admin_user = response['user']
            print(f"   Admin token obtained: {self.admin_token[:20]}...")
        
        # Test student registration
        timestamp = datetime.now().strftime('%H%M%S')
        student_data = {
            "email": f"test_student_{timestamp}@test.com",
            "name": "Test Student",
            "password": "student123"
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
        
        return self.admin_token and self.student_token

    def test_admin_functionality(self):
        """Test admin-specific functionality"""
        print("\n" + "="*50)
        print("TESTING ADMIN FUNCTIONALITY")
        print("="*50)
        
        if not self.admin_token:
            print("❌ No admin token available, skipping admin tests")
            return False
        
        # Test getting existing admin tests first
        success, response = self.run_test(
            "Get Existing Admin Tests",
            "GET",
            "admin/tests",
            200,
            token=self.admin_token
        )
        
        existing_tests = response if success else []
        if existing_tests:
            self.test_id = existing_tests[0]['id']
            print(f"   Using existing test ID: {self.test_id}")
        
        # Test creating a new test
        test_data = {
            "title": "Sample Payment Test",
            "description": "A test for payment integration testing",
            "price": 99.0,
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
            "Create New Test",
            "POST",
            "admin/tests",
            200,
            data=test_data,
            token=self.admin_token
        )
        
        if success and 'id' in response:
            self.test_id = response['id']
            print(f"   New test created with ID: {self.test_id}")
        
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

    def test_delete_test_functionality(self):
        """Test delete test functionality for admin dashboard"""
        print("\n" + "="*50)
        print("TESTING DELETE TEST FUNCTIONALITY")
        print("="*50)
        
        if not self.admin_token:
            print("❌ No admin token available, skipping delete tests")
            return False
        
        # Step 1: Create a test specifically for deletion testing
        test_data = {
            "title": "Test for Deletion",
            "description": "This test will be deleted as part of testing",
            "price": 50.0,
            "duration_minutes": 15,
            "questions": [
                {
                    "question_text": "What is the capital of India?",
                    "options": ["Mumbai", "New Delhi", "Kolkata", "Chennai"],
                    "correct_answer": 1,
                    "explanation": "New Delhi is the capital of India"
                }
            ]
        }
        
        success, response = self.run_test(
            "Create Test for Deletion",
            "POST",
            "admin/tests",
            200,
            data=test_data,
            token=self.admin_token
        )
        
        test_to_delete_id = None
        if success and 'id' in response:
            test_to_delete_id = response['id']
            print(f"   Test created for deletion with ID: {test_to_delete_id}")
        else:
            print("❌ Failed to create test for deletion, skipping delete tests")
            return False
        
        # Step 2: Test unauthorized delete (without admin token)
        success, response = self.run_test(
            "Delete Test Without Authentication",
            "DELETE",
            f"admin/tests/{test_to_delete_id}",
            403  # FastAPI returns 403 for missing authentication
        )
        
        # Step 3: Test delete with student token (should fail)
        if self.student_token:
            success, response = self.run_test(
                "Delete Test With Student Token",
                "DELETE",
                f"admin/tests/{test_to_delete_id}",
                403,  # Should fail - students can't delete tests
                token=self.student_token
            )
        
        # Step 4: Test delete non-existent test
        fake_test_id = "non-existent-test-id-12345"
        success, response = self.run_test(
            "Delete Non-existent Test",
            "DELETE",
            f"admin/tests/{fake_test_id}",
            404,  # Should fail - test not found
            token=self.admin_token
        )
        
        # Step 5: Test successful deletion of test without purchases
        success, response = self.run_test(
            "Delete Test Successfully",
            "DELETE",
            f"admin/tests/{test_to_delete_id}",
            200,  # Should succeed
            token=self.admin_token
        )
        
        if success:
            expected_message = "Test deleted successfully"
            if response.get('message') == expected_message:
                print("   ✅ Test deleted successfully with correct message")
            else:
                print(f"   ⚠️  Unexpected message: {response.get('message')}")
        
        # Step 6: Verify test is actually deleted
        success, response = self.run_test(
            "Verify Test is Deleted",
            "DELETE",
            f"admin/tests/{test_to_delete_id}",
            404,  # Should fail - test no longer exists
            token=self.admin_token
        )
        
        if success:
            print("   ✅ Test confirmed deleted - subsequent delete attempts fail with 404")
        
        # Step 7: Test business logic - create test with simulated purchase
        # Create a test and simulate a purchase to test deletion prevention
        protected_test_data = {
            "title": "Protected Test with Purchase",
            "description": "This test will have a simulated purchase",
            "price": 100.0,
            "duration_minutes": 60,
            "questions": [
                {
                    "question_text": "What is the largest planet in our solar system?",
                    "options": ["Earth", "Jupiter", "Saturn", "Mars"],
                    "correct_answer": 1,
                    "explanation": "Jupiter is the largest planet in our solar system"
                }
            ]
        }
        
        success, response = self.run_test(
            "Create Test for Purchase Protection Test",
            "POST",
            "admin/tests",
            200,
            data=protected_test_data,
            token=self.admin_token
        )
        
        protected_test_id = None
        if success and 'id' in response:
            protected_test_id = response['id']
            print(f"   Protected test created with ID: {protected_test_id}")
            
            # Try to create a purchase order for this test (this will create a purchase record)
            if self.student_token:
                success_purchase, purchase_response = self.run_test(
                    "Create Purchase Order for Protection Test",
                    "POST",
                    f"tests/{protected_test_id}/purchase",
                    200,
                    token=self.student_token
                )
                
                if success_purchase:
                    print("   ✅ Purchase order created - test should now be protected from deletion")
                    
                    # Now try to delete the test - should fail due to purchase
                    success_delete, delete_response = self.run_test(
                        "Try to Delete Test with Purchase (Should Fail)",
                        "DELETE",
                        f"admin/tests/{protected_test_id}",
                        400,  # Should fail with 400 - cannot delete purchased test
                        token=self.admin_token
                    )
                    
                    if success_delete:
                        expected_message = "Cannot delete test that has been purchased by students"
                        if delete_response.get('detail') == expected_message:
                            print("   ✅ Purchase protection working - test cannot be deleted")
                        else:
                            print(f"   ⚠️  Unexpected error message: {delete_response.get('detail')}")
                else:
                    print("   ⚠️  Could not create purchase order for protection test")
        
        # Step 8: Create another test to verify admin can still create tests after deletion
        verification_test_data = {
            "title": "Verification Test After Deletion",
            "description": "This test verifies admin can still create tests",
            "price": 25.0,
            "duration_minutes": 10,
            "questions": [
                {
                    "question_text": "What is 1 + 1?",
                    "options": ["1", "2", "3", "4"],
                    "correct_answer": 1,
                    "explanation": "1 + 1 equals 2"
                }
            ]
        }
        
        success, response = self.run_test(
            "Create Test After Deletion (Verification)",
            "POST",
            "admin/tests",
            200,
            data=verification_test_data,
            token=self.admin_token
        )
        
        # Step 8: Get all admin tests to verify the deleted test is not in the list
        success, response = self.run_test(
            "Get Admin Tests After Deletion",
            "GET",
            "admin/tests",
            200,
            token=self.admin_token
        )
        
        if success:
            test_ids = [test['id'] for test in response]
            if test_to_delete_id not in test_ids:
                print("   ✅ Deleted test confirmed not in admin tests list")
            else:
                print("   ❌ Deleted test still appears in admin tests list")
        
        print("\n📋 Delete test functionality testing completed")
        return True

    def test_password_reset_functionality(self):
        """Test password reset email functionality"""
        print("\n" + "="*50)
        print("TESTING PASSWORD RESET FUNCTIONALITY")
        print("="*50)
        
        # Test 1: Valid Student Email Reset Request
        if self.student_user:
            student_email = self.student_user.get('email')
            if student_email:
                success, response = self.run_test(
                    "Valid Student Email Reset Request",
                    "POST",
                    "forgot-password",
                    200,
                    data={"email": student_email}
                )
                
                if success:
                    expected_message = "If the email exists, a password reset link has been sent"
                    if response.get('message') == expected_message:
                        print("   ✅ Correct security message returned")
                    else:
                        print(f"   ⚠️  Unexpected message: {response.get('message')}")
        
        # Test 2: Invalid Email Reset Request (non-existent email)
        success, response = self.run_test(
            "Invalid Email Reset Request",
            "POST",
            "forgot-password",
            200,  # Should still return 200 for security
            data={"email": "nonexistent@test.com"}
        )
        
        if success:
            expected_message = "If the email exists, a password reset link has been sent"
            if response.get('message') == expected_message:
                print("   ✅ Security feature working - same message for non-existent email")
            else:
                print(f"   ⚠️  Unexpected message: {response.get('message')}")
        
        # Test 3: Admin Email Reset Request (should return success but not send email)
        success, response = self.run_test(
            "Admin Email Reset Request",
            "POST",
            "forgot-password",
            200,
            data={"email": "perspectiveupsc1@gmail.com"}  # Admin email
        )
        
        if success:
            expected_message = "If the email exists, a password reset link has been sent"
            if response.get('message') == expected_message:
                print("   ✅ Admin email handled correctly (returns success but doesn't send)")
            else:
                print(f"   ⚠️  Unexpected message: {response.get('message')}")
        
        # Test 4: Invalid email format
        success, response = self.run_test(
            "Invalid Email Format",
            "POST",
            "forgot-password",
            422,  # Should fail validation
            data={"email": "invalid-email-format"}
        )
        
        # Test 5: Missing email field
        success, response = self.run_test(
            "Missing Email Field",
            "POST",
            "forgot-password",
            422,  # Should fail validation
            data={}
        )
        
        # Test 6: Reset Token Validation with Invalid Token
        success, response = self.run_test(
            "Reset Password with Invalid Token",
            "POST",
            "reset-password",
            400,  # Should fail with invalid token
            data={
                "email": "test@example.com",
                "reset_token": "invalid_token_12345",
                "new_password": "newpassword123"
            }
        )
        
        if success:
            expected_message = "Invalid or expired reset token"
            if response.get('detail') == expected_message:
                print("   ✅ Invalid token properly rejected")
            else:
                print(f"   ⚠️  Unexpected error message: {response.get('detail')}")
        
        # Test 7: Reset Password with Missing Fields
        success, response = self.run_test(
            "Reset Password with Missing Fields",
            "POST",
            "reset-password",
            422,  # Should fail validation
            data={
                "email": "test@example.com"
                # Missing reset_token and new_password
            }
        )
        
        print("\n📧 Check backend logs for email sending confirmation...")
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
        self.test_delete_test_functionality()
        self.test_password_reset_functionality()
        
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

    def run_delete_tests_only(self):
        """Run only delete test functionality tests"""
        print("🗑️ Starting Delete Test Functionality Testing")
        print(f"Base URL: {self.base_url}")
        
        # First get authentication tokens
        print("\n📋 Setting up authentication for delete tests...")
        self.test_authentication()
        
        # Run delete tests
        self.test_delete_test_functionality()
        
        # Print final results
        print("\n" + "="*50)
        print("DELETE TEST FUNCTIONALITY RESULTS")
        print("="*50)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All delete test functionality tests passed!")
            return 0
        else:
            print(f"❌ {self.tests_run - self.tests_passed} tests failed")
            return 1

    def run_password_reset_tests_only(self):
        """Run only password reset tests"""
        print("🔐 Starting Password Reset Testing")
        print(f"Base URL: {self.base_url}")
        
        # First get authentication tokens
        print("\n📋 Setting up authentication for password reset tests...")
        self.test_authentication()
        
        # Run password reset tests
        self.test_password_reset_functionality()
        
        # Print final results
        print("\n" + "="*50)
        print("PASSWORD RESET TEST RESULTS")
        print("="*50)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All password reset tests passed!")
            return 0
        else:
            print(f"❌ {self.tests_run - self.tests_passed} tests failed")
            return 1

def main():
    tester = TestPlatformAPITester()
    return tester.run_all_tests()

def test_delete_functionality_only():
    """Function to run only delete test functionality tests"""
    tester = TestPlatformAPITester()
    return tester.run_delete_tests_only()

def test_password_reset_only():
    """Function to run only password reset tests"""
    tester = TestPlatformAPITester()
    return tester.run_password_reset_tests_only()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "password-reset":
        sys.exit(test_password_reset_only())
    elif len(sys.argv) > 1 and sys.argv[1] == "delete-tests":
        sys.exit(test_delete_functionality_only())
    else:
        sys.exit(main())