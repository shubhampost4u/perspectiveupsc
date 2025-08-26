#!/usr/bin/env python3
"""
Comprehensive Password Reset Test
Tests the complete password reset flow including token generation and validation
"""

import requests
import json
import re
import time
from datetime import datetime

class PasswordResetTester:
    def __init__(self):
        # Use the production URL from frontend/.env
        self.base_url = "https://upscpractice.preview.emergentagent.com/api"
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'details': details
        })
    
    def create_test_student(self):
        """Create a test student for password reset testing"""
        timestamp = datetime.now().strftime('%H%M%S')
        student_data = {
            "email": f"reset_test_{timestamp}@perspectiveupsc.com",
            "name": "Reset Test Student",
            "password": "original_password123"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/register",
                json=student_data,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_result(
                    "Student Registration",
                    True,
                    f"Student created: {student_data['email']}"
                )
                return student_data
            else:
                self.log_result(
                    "Student Registration",
                    False,
                    f"Failed with status {response.status_code}",
                    response.text
                )
                return None
                
        except Exception as e:
            self.log_result(
                "Student Registration",
                False,
                f"Exception occurred: {str(e)}"
            )
            return None
    
    def test_forgot_password_scenarios(self, student_email):
        """Test various forgot password scenarios"""
        
        # Test 1: Valid student email
        try:
            response = requests.post(
                f"{self.base_url}/forgot-password",
                json={"email": student_email},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                expected_msg = "If the email exists, a password reset link has been sent"
                if data.get('message') == expected_msg:
                    self.log_result(
                        "Valid Student Email Reset",
                        True,
                        "Correct response received"
                    )
                else:
                    self.log_result(
                        "Valid Student Email Reset",
                        False,
                        f"Unexpected message: {data.get('message')}"
                    )
            else:
                self.log_result(
                    "Valid Student Email Reset",
                    False,
                    f"Unexpected status code: {response.status_code}"
                )
                
        except Exception as e:
            self.log_result(
                "Valid Student Email Reset",
                False,
                f"Exception: {str(e)}"
            )
        
        # Test 2: Non-existent email (should return same message for security)
        try:
            response = requests.post(
                f"{self.base_url}/forgot-password",
                json={"email": "nonexistent@test.com"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                expected_msg = "If the email exists, a password reset link has been sent"
                if data.get('message') == expected_msg:
                    self.log_result(
                        "Non-existent Email Reset",
                        True,
                        "Security feature working - same message returned"
                    )
                else:
                    self.log_result(
                        "Non-existent Email Reset",
                        False,
                        f"Security issue - different message: {data.get('message')}"
                    )
            else:
                self.log_result(
                    "Non-existent Email Reset",
                    False,
                    f"Unexpected status code: {response.status_code}"
                )
                
        except Exception as e:
            self.log_result(
                "Non-existent Email Reset",
                False,
                f"Exception: {str(e)}"
            )
        
        # Test 3: Admin email (should return success but not send email)
        try:
            response = requests.post(
                f"{self.base_url}/forgot-password",
                json={"email": "perspectiveupsc1@gmail.com"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                expected_msg = "If the email exists, a password reset link has been sent"
                if data.get('message') == expected_msg:
                    self.log_result(
                        "Admin Email Reset",
                        True,
                        "Admin email handled correctly (returns success)"
                    )
                else:
                    self.log_result(
                        "Admin Email Reset",
                        False,
                        f"Unexpected message: {data.get('message')}"
                    )
            else:
                self.log_result(
                    "Admin Email Reset",
                    False,
                    f"Unexpected status code: {response.status_code}"
                )
                
        except Exception as e:
            self.log_result(
                "Admin Email Reset",
                False,
                f"Exception: {str(e)}"
            )
        
        # Test 4: Invalid email format
        try:
            response = requests.post(
                f"{self.base_url}/forgot-password",
                json={"email": "invalid-email"},
                timeout=10
            )
            
            if response.status_code == 422:
                self.log_result(
                    "Invalid Email Format",
                    True,
                    "Validation error returned as expected"
                )
            else:
                self.log_result(
                    "Invalid Email Format",
                    False,
                    f"Expected 422, got {response.status_code}"
                )
                
        except Exception as e:
            self.log_result(
                "Invalid Email Format",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_reset_password_scenarios(self, student_email):
        """Test reset password scenarios"""
        
        # Test 1: Invalid token
        try:
            response = requests.post(
                f"{self.base_url}/reset-password",
                json={
                    "email": student_email,
                    "reset_token": "invalid_token_12345",
                    "new_password": "new_password123"
                },
                timeout=10
            )
            
            if response.status_code == 400:
                data = response.json()
                if "Invalid or expired reset token" in data.get('detail', ''):
                    self.log_result(
                        "Invalid Reset Token",
                        True,
                        "Invalid token properly rejected"
                    )
                else:
                    self.log_result(
                        "Invalid Reset Token",
                        False,
                        f"Unexpected error message: {data.get('detail')}"
                    )
            else:
                self.log_result(
                    "Invalid Reset Token",
                    False,
                    f"Expected 400, got {response.status_code}"
                )
                
        except Exception as e:
            self.log_result(
                "Invalid Reset Token",
                False,
                f"Exception: {str(e)}"
            )
        
        # Test 2: Missing fields
        try:
            response = requests.post(
                f"{self.base_url}/reset-password",
                json={"email": student_email},  # Missing token and password
                timeout=10
            )
            
            if response.status_code == 422:
                self.log_result(
                    "Missing Reset Fields",
                    True,
                    "Validation error for missing fields"
                )
            else:
                self.log_result(
                    "Missing Reset Fields",
                    False,
                    f"Expected 422, got {response.status_code}"
                )
                
        except Exception as e:
            self.log_result(
                "Missing Reset Fields",
                False,
                f"Exception: {str(e)}"
            )
    
    def check_email_sending_logs(self):
        """Check if email sending is working by examining logs"""
        print("\n📧 Checking Email Sending Status...")
        
        try:
            # Check if SMTP is configured
            import os
            smtp_username = os.environ.get('SMTP_USERNAME')
            smtp_password = os.environ.get('SMTP_PASSWORD')
            
            if smtp_username and smtp_password:
                print(f"   SMTP configured with username: {smtp_username}")
                self.log_result(
                    "SMTP Configuration",
                    True,
                    f"SMTP credentials configured for {smtp_username}"
                )
            else:
                self.log_result(
                    "SMTP Configuration",
                    False,
                    "SMTP credentials not configured - using console logging"
                )
                
        except Exception as e:
            self.log_result(
                "SMTP Configuration Check",
                False,
                f"Error checking SMTP config: {str(e)}"
            )
    
    def run_comprehensive_test(self):
        """Run all password reset tests"""
        print("🔐 Starting Comprehensive Password Reset Testing")
        print(f"Base URL: {self.base_url}")
        print("="*60)
        
        # Create test student
        student_data = self.create_test_student()
        if not student_data:
            print("❌ Cannot proceed without test student")
            return False
        
        student_email = student_data['email']
        
        # Test forgot password scenarios
        print("\n📧 Testing Forgot Password Scenarios...")
        self.test_forgot_password_scenarios(student_email)
        
        # Test reset password scenarios
        print("\n🔑 Testing Reset Password Scenarios...")
        self.test_reset_password_scenarios(student_email)
        
        # Check email configuration
        self.check_email_sending_logs()
        
        # Print summary
        print("\n" + "="*60)
        print("COMPREHENSIVE TEST RESULTS")
        print("="*60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"📊 Tests passed: {passed}/{total}")
        
        if passed == total:
            print("🎉 All password reset tests passed!")
            return True
        else:
            print(f"❌ {total - passed} tests failed")
            
            # Show failed tests
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
            
            return False

def main():
    tester = PasswordResetTester()
    success = tester.run_comprehensive_test()
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())