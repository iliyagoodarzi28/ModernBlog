"""
Specific Playwright test for Django logout functionality
Tests the accounts/logout/ endpoint
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright
import django
from django.conf import settings

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import CustomUser


def test_logout_functionality():
    """Test logout functionality specifically"""
    
    # Create test user if it doesn't exist
    test_email = "test@example.com"
    test_password = "TestPassword123!"
    
    if not CustomUser.objects.filter(email=test_email).exists():
        CustomUser.objects.create_user(
            email=test_email,
            username="testuser",
            password=test_password,
            full_name="Test User"
        )
        print("Test user created")
    else:
        print("Test user already exists")
    
    # Start Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            print("Testing Logout Functionality")
            print("=" * 50)
            
            # Step 1: Login first
            print("Step 1: Logging in...")
            page.goto("http://localhost:8000/accounts/login/")
            
            # Fill login form
            page.fill('input[name="username"]', test_email)
            page.fill('input[name="password"]', test_password)
            page.click('button[type="submit"]')
            
            # Wait for login to complete
            page.wait_for_load_state("networkidle")
            
            # Check if logged in
            current_url = page.url
            print(f"   After login URL: {current_url}")
            
            if "login" not in current_url:
                print("   Login successful!")
                
                # Step 2: Check user is authenticated
                print("\nStep 2: Checking authentication state...")
                
                # Look for user profile button
                user_button = page.locator('button:has-text("testuser")')
                if user_button.is_visible():
                    print("   User profile button visible - user is authenticated")
                    
                    # Step 3: Test logout via user menu
                    print("\nStep 3: Testing logout via user menu...")
                    user_button.click()
                    
                    # Wait for dropdown to appear
                    page.wait_for_timeout(1000)
                    
                    # Look for logout link
                    logout_link = page.locator('a:has-text("Sign out")')
                    if logout_link.is_visible():
                        print("   Logout link found in dropdown menu")
                        logout_link.click()
                        
                        # Wait for logout to complete
                        page.wait_for_load_state("networkidle")
                        
                        # Check logout result
                        logout_url = page.url
                        print(f"   After logout URL: {logout_url}")
                        
                        # Check for logout success message
                        try:
                            success_message = page.locator('.alert-info').text_content()
                            print(f"   Logout message: {success_message}")
                        except:
                            print("   No logout message found")
                        
                        # Check if user is still authenticated
                        user_button_after = page.locator('button:has-text("testuser")')
                        if user_button_after.is_visible():
                            print("   WARNING: User still appears to be authenticated")
                        else:
                            print("   SUCCESS: User successfully logged out")
                            
                    else:
                        print("   ERROR: Logout link not found in dropdown")
                        
                else:
                    print("   ERROR: User profile button not found")
                    
                # Step 4: Test direct logout URL
                print("\nStep 4: Testing direct logout URL...")
                
                # Login again for this test
                page.goto("http://localhost:8000/accounts/login/")
                page.fill('input[name="username"]', test_email)
                page.fill('input[name="password"]', test_password)
                page.click('button[type="submit"]')
                page.wait_for_load_state("networkidle")
                
                # Navigate directly to logout URL
                print("   Navigating directly to /accounts/logout/")
                page.goto("http://localhost:8000/accounts/logout/")
                page.wait_for_load_state("networkidle")
                
                logout_direct_url = page.url
                print(f"   After direct logout URL: {logout_direct_url}")
                
                # Check if redirected to login page
                if "login" in logout_direct_url:
                    print("   SUCCESS: Direct logout redirected to login page")
                else:
                    print(f"   INFO: Direct logout redirected to: {logout_direct_url}")
                
                # Step 5: Test logout with POST request
                print("\nStep 5: Testing logout with POST request...")
                
                # Login again
                page.goto("http://localhost:8000/accounts/login/")
                page.fill('input[name="username"]', test_email)
                page.fill('input[name="password"]', test_password)
                page.click('button[type="submit"]')
                page.wait_for_load_state("networkidle")
                
                # Get CSRF token
                csrf_token = page.locator('input[name="csrfmiddlewaretoken"]').get_attribute('value')
                print(f"   CSRF token: {csrf_token[:20]}...")
                
                # Make POST request to logout
                response = page.request.post(
                    "http://localhost:8000/accounts/logout/",
                    data={"csrfmiddlewaretoken": csrf_token}
                )
                
                print(f"   POST logout response status: {response.status}")
                
                if response.status == 200:
                    print("   SUCCESS: POST logout request successful")
                else:
                    print(f"   INFO: POST logout response: {response.status}")
                
            else:
                print("   ERROR: Login failed")
            
            print("\nLogout Test Completed!")
            
        except Exception as e:
            print(f"Test failed with error: {str(e).encode('ascii', 'ignore').decode('ascii')}")
            raise
        
        finally:
            browser.close()


def main():
    """Main function to run the logout test"""
    print("Starting Logout Functionality Test")
    print("=" * 50)
    
    # Check if Django server is running
    try:
        import requests
        response = requests.get("http://localhost:8000/", timeout=5)
        print("Django server is running")
    except:
        print("Django server is not running!")
        print("Please start the server with: python manage.py runserver")
        return
    
    # Run the test
    test_logout_functionality()


if __name__ == "__main__":
    main()
