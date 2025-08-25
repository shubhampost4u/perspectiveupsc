import requests
import sys
import json
from datetime import datetime

class SecurityUpdateTester:
    def __init__(self, base_url=None):
        if base_url is None:
            # Use the public endpoint for testing
            base_url = "https://testify-5.preview.emergentagent.com/api"
        self.base_url = base_url
        self.admin_token = None
        self.student_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.security_issues = []

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        
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
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)}")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {json.dumps(error_detail, indent=2)}")
                except:
                    print(f"   Response text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_security_update_registration(self):
        """Test the security update: student-only registration"""
        print("\n" + "="*60)
        print("TESTING SECURITY UPDATE: STUDENT-ONLY REGISTRATION")
        print("="*60)
        
        timestamp = datetime.now().strftime('%H%M%S%f')
        
        # Test 1: Try to register as admin (should be blocked/forced to student)
        print("\n🔒 Test 1: Attempt admin registration (should create student)")
        admin_attempt_data = {
            "email": f"test_admin_{timestamp}@test.com",
            "name": "Test Admin Attempt",
            "password": "admin123",
            "role": "admin"  # This should be ignored
        }
        
        success, response = self.run_test(
            "Admin Registration Attempt",
            "POST",
            "register",
            200,
            data=admin_attempt_data
        )
        
        if success:
            if response.get('role') == 'student':
                print("✅ SECURITY: Admin registration correctly forced to student role")
            else:
                print(f"❌ SECURITY ISSUE: Registration created role '{response.get('role')}' instead of 'student'")
                self.security_issues.append("Admin registration not properly blocked")
        
        # Test 2: Register normal student (should work)
        print("\n👨‍🎓 Test 2: Normal student registration")
        student_data = {
            "email": f"test_student_{timestamp}@test.com",
            "name": "Test Student",
            "password": "student123"
            # No role field - should default to student
        }
        
        success, response = self.run_test(
            "Student Registration",
            "POST",
            "register",
            200,
            data=student_data
        )
        
        if success:
            if response.get('role') == 'student':
                print("✅ SECURITY: Student registration works correctly")
            else:
                print(f"❌ SECURITY ISSUE: Student registration created role '{response.get('role')}'")
                self.security_issues.append("Student registration role incorrect")
        
        # Test 3: Try registration with explicit student role
        print("\n👨‍🎓 Test 3: Explicit student role registration")
        explicit_student_data = {
            "email": f"test_student_explicit_{timestamp}@test.com",
            "name": "Test Student Explicit",
            "password": "student123",
            "role": "student"
        }
        
        success, response = self.run_test(
            "Explicit Student Registration",
            "POST",
            "register",
            200,
            data=explicit_student_data
        )
        
        if success:
            if response.get('role') == 'student':
                print("✅ SECURITY: Explicit student registration works correctly")
            else:
                print(f"❌ SECURITY ISSUE: Explicit student registration created role '{response.get('role')}'")
                self.security_issues.append("Explicit student registration role incorrect")
        
        # Test 4: Try registration with invalid role
        print("\n🚫 Test 4: Invalid role registration")
        invalid_role_data = {
            "email": f"test_invalid_{timestamp}@test.com",
            "name": "Test Invalid Role",
            "password": "test123",
            "role": "superuser"  # Invalid role
        }
        
        success, response = self.run_test(
            "Invalid Role Registration",
            "POST",
            "register",
            200,
            data=invalid_role_data
        )
        
        if success:
            if response.get('role') == 'student':
                print("✅ SECURITY: Invalid role correctly forced to student")
            else:
                print(f"❌ SECURITY ISSUE: Invalid role created '{response.get('role')}' instead of 'student'")
                self.security_issues.append("Invalid role not properly handled")

    def test_existing_admin_access(self):
        """Test that existing admin account still works"""
        print("\n" + "="*60)
        print("TESTING EXISTING ADMIN ACCESS")
        print("="*60)
        
        # Test admin login
        admin_login = {
            "email": "admin@test.com",
            "password": "admin123"
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
            admin_user = response.get('user', {})
            print(f"✅ Admin login successful")
            print(f"   Admin role: {admin_user.get('role')}")
            print(f"   Admin email: {admin_user.get('email')}")
            
            if admin_user.get('role') == 'admin':
                print("✅ SECURITY: Existing admin maintains admin role")
            else:
                print(f"❌ SECURITY ISSUE: Admin role is '{admin_user.get('role')}' instead of 'admin'")
                self.security_issues.append("Existing admin lost admin privileges")
        else:
            print("❌ SECURITY ISSUE: Existing admin cannot login")
            self.security_issues.append("Existing admin login failed")

    def test_admin_functionality_access(self):
        """Test that admin functions are still accessible"""
        print("\n" + "="*60)
        print("TESTING ADMIN FUNCTIONALITY ACCESS")
        print("="*60)
        
        if not self.admin_token:
            print("❌ No admin token available, skipping admin functionality tests")
            return False
        
        # Test admin endpoints
        success, response = self.run_test(
            "Admin Get Students",
            "GET",
            "admin/students",
            200,
            token=self.admin_token
        )
        
        if success:
            print("✅ SECURITY: Admin can access student list")
        else:
            print("❌ SECURITY ISSUE: Admin cannot access student list")
            self.security_issues.append("Admin lost access to student list")
        
        success, response = self.run_test(
            "Admin Get Tests",
            "GET",
            "admin/tests",
            200,
            token=self.admin_token
        )
        
        if success:
            print("✅ SECURITY: Admin can access admin tests")
        else:
            print("❌ SECURITY ISSUE: Admin cannot access admin tests")
            self.security_issues.append("Admin lost access to admin tests")

    def test_student_cannot_access_admin(self):
        """Test that new student accounts cannot access admin functions"""
        print("\n" + "="*60)
        print("TESTING STUDENT ACCESS RESTRICTIONS")
        print("="*60)
        
        # First create and login a student
        timestamp = datetime.now().strftime('%H%M%S%f')
        student_data = {
            "email": f"security_test_student_{timestamp}@test.com",
            "name": "Security Test Student",
            "password": "student123"
        }
        
        success, response = self.run_test(
            "Create Test Student",
            "POST",
            "register",
            200,
            data=student_data
        )
        
        if not success:
            print("❌ Could not create test student")
            return False
        
        # Login the student
        student_login = {
            "email": student_data["email"],
            "password": student_data["password"]
        }
        
        success, response = self.run_test(
            "Test Student Login",
            "POST",
            "login",
            200,
            data=student_login
        )
        
        if success and 'access_token' in response:
            student_token = response['access_token']
            print("✅ Test student login successful")
            
            # Test student trying to access admin endpoints (should fail)
            success, response = self.run_test(
                "Student Access Admin Students (Should Fail)",
                "GET",
                "admin/students",
                403,
                token=student_token
            )
            
            if success:
                print("✅ SECURITY: Student correctly blocked from admin/students")
            else:
                print("❌ SECURITY ISSUE: Student can access admin/students")
                self.security_issues.append("Student can access admin endpoints")
            
            success, response = self.run_test(
                "Student Access Admin Tests (Should Fail)",
                "GET",
                "admin/tests",
                403,
                token=student_token
            )
            
            if success:
                print("✅ SECURITY: Student correctly blocked from admin/tests")
            else:
                print("❌ SECURITY ISSUE: Student can access admin/tests")
                self.security_issues.append("Student can access admin test endpoints")
        else:
            print("❌ Test student login failed")

    def test_role_based_access_control(self):
        """Test that role-based access control still works"""
        print("\n" + "="*60)
        print("TESTING ROLE-BASED ACCESS CONTROL")
        print("="*60)
        
        # Test unauthenticated access (should fail)
        success, response = self.run_test(
            "Unauthenticated Admin Access (Should Fail)",
            "GET",
            "admin/students",
            401
        )
        
        if success:
            print("✅ SECURITY: Unauthenticated access correctly blocked")
        else:
            print("❌ SECURITY ISSUE: Unauthenticated access not properly blocked")
            self.security_issues.append("Unauthenticated access not blocked")

    def run_security_tests(self):
        """Run all security tests"""
        print("🔒 Starting Security Update Testing")
        print(f"Base URL: {self.base_url}")
        print("="*80)
        
        # Run security test suites
        self.test_security_update_registration()
        self.test_existing_admin_access()
        self.test_admin_functionality_access()
        self.test_student_cannot_access_admin()
        self.test_role_based_access_control()
        
        # Print final results
        print("\n" + "="*80)
        print("SECURITY TEST RESULTS")
        print("="*80)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        if self.security_issues:
            print(f"\n🚨 SECURITY ISSUES FOUND ({len(self.security_issues)}):")
            for i, issue in enumerate(self.security_issues, 1):
                print(f"   {i}. {issue}")
        else:
            print("\n🎉 NO SECURITY ISSUES FOUND!")
        
        if self.tests_passed == self.tests_run and not self.security_issues:
            print("\n✅ ALL SECURITY TESTS PASSED!")
            return 0
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"\n❌ {failed_tests} tests failed, {len(self.security_issues)} security issues found")
            return 1

def main():
    tester = SecurityUpdateTester()
    return tester.run_security_tests()

if __name__ == "__main__":
    sys.exit(main())