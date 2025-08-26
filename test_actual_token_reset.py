#!/usr/bin/env python3
"""
Test password reset with actual generated token
"""

import requests
import json

def test_actual_token_reset():
    base_url = "https://upscpractice.preview.emergentagent.com/api"
    
    # Use the token and email from the logs
    test_email = "complete_test_060824@perspectiveupsc.com"
    reset_token = "yo3Lf29ls5L-ZtjQI5wCcYbfRuazVm9EcmcmVQkF2Eo"
    new_password = "new_secure_password123"
    
    print("🔐 Testing Password Reset with Actual Token")
    print("="*50)
    print(f"Email: {test_email}")
    print(f"Token: {reset_token[:20]}...")
    print(f"New Password: {new_password}")
    
    # Test password reset with actual token
    print(f"\n🔑 Attempting password reset with actual token...")
    try:
        reset_response = requests.post(
            f"{base_url}/reset-password",
            json={
                "email": test_email,
                "reset_token": reset_token,
                "new_password": new_password
            },
            timeout=10
        )
        
        print(f"Status Code: {reset_response.status_code}")
        
        if reset_response.status_code == 200:
            response_data = reset_response.json()
            print("✅ Password reset successful!")
            print(f"Response: {response_data}")
            
            # Test login with new password
            print(f"\n🧪 Testing login with new password...")
            login_response = requests.post(
                f"{base_url}/login",
                json={"email": test_email, "password": new_password},
                timeout=10
            )
            
            if login_response.status_code == 200:
                print("✅ Login with new password successful!")
                print("🎉 Complete password reset flow working perfectly!")
                return True
            else:
                print(f"❌ Login with new password failed: {login_response.status_code}")
                try:
                    error_data = login_response.json()
                    print(f"Error: {error_data}")
                except:
                    print(f"Response text: {login_response.text}")
                return False
                
        else:
            print(f"❌ Password reset failed: {reset_response.status_code}")
            try:
                error_data = reset_response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Response text: {reset_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during password reset: {e}")
        return False

if __name__ == "__main__":
    success = test_actual_token_reset()
    if success:
        print("\n🎯 CONCLUSION: Password reset functionality is FULLY WORKING!")
    else:
        print("\n❌ CONCLUSION: Password reset has issues that need attention.")