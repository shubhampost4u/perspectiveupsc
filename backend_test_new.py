import requests
import sys
import json
import io
import pandas as pd
from datetime import datetime

class PerspectiveUPSCAPITester:
    def __init__(self, base_url=None):
        if base_url is None:
            # Use the production URL for PerspectiveUPSC
            base_url = "https://perspectiveupsc.com/api"
        self.base_url = base_url
        self.admin_token = None
        self.student_token = None
        self.admin_user = None
        self.student_user = None
        self.test_id = None
        self.reset_token = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        # Don't set Content-Type for file uploads
        if not files:
            headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, headers={k:v for k,v in headers.items() if k != 'Content-Type'}, timeout=10)
                else:
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
        print("\n" + "="*60)
        print("TESTING BASIC CONNECTIVITY")
        print("="*60)
        
        success, response = self.run_test(
            "Basic API Root",
            "GET",
            "",
            200
        )
        return success

    def test_perspectiveupsc_admin_login(self):
        """Test PerspectiveUPSC admin login with provided credentials"""
        print("\n" + "="*60)
        print("TESTING PERSPECTIVEUPSC ADMIN LOGIN")
        print("="*60)
        
        # Test PerspectiveUPSC admin login
        admin_login = {
            "email": "perspectiveupsc1@gmail.com",
            "password": "perspective@2025"
        }
        
        success, response = self.run_test(
            "PerspectiveUPSC Admin Login",
            "POST",
            "login",
            200,
            data=admin_login
        )
        
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            self.admin_user = response.get('user', {})
            print(f"   Admin token obtained: {self.admin_token[:20]}...")
            print(f"   Admin user: {self.admin_user.get('name', 'Unknown')} ({self.admin_user.get('role', 'Unknown')})")
            return True
        else:
            print("❌ Failed to login with PerspectiveUPSC admin credentials")
            return False

    def test_bulk_upload_features(self):
        """Test new bulk upload features"""
        print("\n" + "="*60)
        print("TESTING BULK UPLOAD FEATURES")
        print("="*60)
        
        if not self.admin_token:
            print("❌ No admin token available, skipping bulk upload tests")
            return False
        
        # Test bulk upload format endpoint
        success, response = self.run_test(
            "Get Bulk Upload Format",
            "GET",
            "admin/bulk-upload-format",
            200,
            token=self.admin_token
        )
        
        if success:
            print(f"   Format requirements: {response.get('required_columns', [])}")
        
        # Create sample Excel data for testing
        sample_data = {
            'question_text': [
                'What is the capital of India?',
                'Which planet is known as the Red Planet?',
                'What is 15 + 25?'
            ],
            'option_a': ['Mumbai', 'Venus', '35'],
            'option_b': ['New Delhi', 'Mars', '40'],
            'option_c': ['Kolkata', 'Jupiter', '45'],
            'option_d': ['Chennai', 'Saturn', '50'],
            'correct_answer': ['B', 'B', 'B'],
            'explanation': [
                'New Delhi is the capital city of India.',
                'Mars is known as the Red Planet due to its reddish appearance.',
                '15 + 25 = 40'
            ]
        }
        
        # Create Excel file in memory
        df = pd.DataFrame(sample_data)
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        
        # Test bulk upload questions
        files = {
            'file': ('test_questions.xlsx', excel_buffer.getvalue(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        }
        
        success, response = self.run_test(
            "Bulk Upload Questions",
            "POST",
            "admin/bulk-upload-questions",
            200,
            token=self.admin_token,
            files=files
        )
        
        if success:
            print(f"   Questions processed: {response.get('count', 0)}")
        
        return True

    def test_password_recovery_features(self):
        """Test password recovery features"""
        print("\n" + "="*60)
        print("TESTING PASSWORD RECOVERY FEATURES")
        print("="*60)
        
        # Create a test student for password recovery
        timestamp = datetime.now().strftime('%H%M%S')
        student_data = {
            "email": f"test_student_{timestamp}@test.com",
            "name": "Test Student",
            "password": "student123"
        }
        
        success, response = self.run_test(
            "Register Test Student",
            "POST",
            "register",
            200,
            data=student_data
        )
        
        if not success:
            print("❌ Failed to register test student for password recovery")
            return False
        
        # Test forgot password
        forgot_data = {
            "email": student_data["email"]
        }
        
        success, response = self.run_test(
            "Forgot Password Request",
            "POST",
            "forgot-password",
            200,
            data=forgot_data
        )
        
        if success:
            print("   Password reset email would be sent (check backend logs for token)")
        
        # Note: In a real test, we would need to extract the reset token from email/logs
        # For now, we'll test with a dummy token to verify the endpoint structure
        reset_data = {
            "email": student_data["email"],
            "reset_token": "dummy_token_for_testing",
            "new_password": "newpassword123"
        }
        
        success, response = self.run_test(
            "Reset Password (Expected to fail with dummy token)",
            "POST",
            "reset-password",
            400,  # Expected to fail with invalid token
            data=reset_data
        )
        
        return True

    def test_student_solutions_access(self):
        """Test student solutions access after completing tests"""
        print("\n" + "="*60)
        print("TESTING STUDENT SOLUTIONS ACCESS")
        print("="*60)
        
        if not self.admin_token:
            print("❌ No admin token available, skipping solutions tests")
            return False
        
        # First create a test with solutions
        test_data = {
            "title": "Sample UPSC Test with Solutions",
            "description": "A test with detailed explanations",
            "price": 99.99,
            "duration_minutes": 60,
            "questions": [
                {
                    "question_text": "Who was the first President of India?",
                    "options": ["Mahatma Gandhi", "Dr. Rajendra Prasad", "Jawaharlal Nehru", "Sardar Patel"],
                    "correct_answer": 1,
                    "explanation": "Dr. Rajendra Prasad was the first President of India, serving from 1950 to 1962."
                },
                {
                    "question_text": "In which year did India gain independence?",
                    "options": ["1946", "1947", "1948", "1949"],
                    "correct_answer": 1,
                    "explanation": "India gained independence on August 15, 1947, from British colonial rule."
                }
            ]
        }
        
        success, response = self.run_test(
            "Create Test with Solutions",
            "POST",
            "admin/tests",
            200,
            data=test_data,
            token=self.admin_token
        )
        
        if success and 'id' in response:
            test_id = response['id']
            print(f"   Test created with ID: {test_id}")
            
            # Create a student and complete the test
            timestamp = datetime.now().strftime('%H%M%S')
            student_data = {
                "email": f"solutions_student_{timestamp}@test.com",
                "name": "Solutions Test Student",
                "password": "student123"
            }
            
            success, response = self.run_test(
                "Register Solutions Test Student",
                "POST",
                "register",
                200,
                data=student_data
            )
            
            if success:
                # Login student
                student_login = {
                    "email": student_data["email"],
                    "password": student_data["password"]
                }
                
                success, response = self.run_test(
                    "Login Solutions Test Student",
                    "POST",
                    "login",
                    200,
                    data=student_login
                )
                
                if success and 'access_token' in response:
                    student_token = response['access_token']
                    
                    # Purchase test
                    success, response = self.run_test(
                        "Purchase Test for Solutions",
                        "POST",
                        f"tests/{test_id}/purchase",
                        200,
                        token=student_token
                    )
                    
                    if success:
                        # Submit test
                        submit_data = {
                            "answers": [1, 0],  # One correct, one incorrect
                            "time_taken_minutes": 30
                        }
                        
                        success, response = self.run_test(
                            "Submit Test for Solutions",
                            "POST",
                            f"tests/{test_id}/submit",
                            200,
                            data=submit_data,
                            token=student_token
                        )
                        
                        if success:
                            # Now test solutions access
                            success, response = self.run_test(
                                "Get Test Solutions",
                                "GET",
                                f"test-solutions/{test_id}",
                                200,
                                token=student_token
                            )
                            
                            if success:
                                print(f"   Solutions retrieved for {response.get('total_questions', 0)} questions")
                                print(f"   Student score: {response.get('student_score', 0)}/{response.get('total_questions', 0)}")
                                solutions = response.get('solutions', [])
                                if solutions:
                                    print(f"   First solution explanation: {solutions[0].get('explanation', 'No explanation')[:50]}...")
        
        return True

    def test_admin_functionality(self):
        """Test admin-specific functionality"""
        print("\n" + "="*60)
        print("TESTING ADMIN FUNCTIONALITY")
        print("="*60)
        
        if not self.admin_token:
            print("❌ No admin token available, skipping admin tests")
            return False
        
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
        print("\n" + "="*60)
        print("TESTING STUDENT FUNCTIONALITY")
        print("="*60)
        
        # Test getting available tests (no auth required)
        success, response = self.run_test(
            "Get Available Tests",
            "GET",
            "tests",
            200
        )
        
        if success:
            print(f"   Available tests: {len(response) if isinstance(response, list) else 0}")
        
        return True

    def test_authorization(self):
        """Test authorization and access control"""
        print("\n" + "="*60)
        print("TESTING AUTHORIZATION")
        print("="*60)
        
        # Test unauthenticated access to admin endpoints
        success, response = self.run_test(
            "Unauthenticated Admin Access (Should Fail)",
            "GET",
            "admin/tests",
            401
        )
        
        success, response = self.run_test(
            "Unauthenticated Bulk Upload Format (Should Fail)",
            "GET",
            "admin/bulk-upload-format",
            401
        )
        
        return True

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting PerspectiveUPSC API Testing")
        print(f"Base URL: {self.base_url}")
        
        # Run test suites
        self.test_basic_connectivity()
        self.test_perspectiveupsc_admin_login()
        self.test_bulk_upload_features()
        self.test_password_recovery_features()
        self.test_student_solutions_access()
        self.test_admin_functionality()
        self.test_student_functionality()
        self.test_authorization()
        
        # Print final results
        print("\n" + "="*60)
        print("FINAL RESULTS")
        print("="*60)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print(f"❌ {self.tests_run - self.tests_passed} tests failed")
            return 1

def main():
    tester = PerspectiveUPSCAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())