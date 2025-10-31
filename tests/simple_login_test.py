"""
Simple Playwright test for Django login functionality
This is a basic test that can be run immediately
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


def test_login_functionality():
    """Test basic login functionality"""
    
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
        browser = p.chromium.launch(headless=False)  # Set to True for headless mode
        page = browser.new_page()
        
        try:
            print("Navigating to login page...")
            page.goto("http://localhost:8000/accounts/login/")
            
            # Check if page loaded correctly
            print("Checking page elements...")
            
            # Check title
            title = page.title()
            print(f"   Page title: {title}")
            
            # Check main heading
            heading = page.locator("h2").text_content()
            print(f"   Main heading: {heading}")
            
            # Check form elements
            username_field = page.locator('input[name="username"]')
            password_field = page.locator('input[name="password"]')
            submit_button = page.locator('button[type="submit"]').first
            
            print(f"   Username field visible: {username_field.is_visible()}")
            print(f"   Password field visible: {password_field.is_visible()}")
            print(f"   Submit button visible: {submit_button.is_visible()}")
            
            # Test login
            print("Testing login...")
            
            # Fill form
            username_field.fill(test_email)
            password_field.fill(test_password)
            
            # Submit form
            submit_button.click()
            
            # Wait for navigation
            page.wait_for_load_state("networkidle")
            
            # Check if redirected to home page
            current_url = page.url
            print(f"   Current URL after login: {current_url}")
            
            if "localhost:8000/" in current_url and "login" not in current_url:
                print("Login successful! Redirected to home page")
                
                # Check for success message
                try:
                    success_message = page.locator('.alert-success').text_content()
                    print(f"   Success message: {success_message}")
                except:
                    print("   No success message found")
                
                # Test logout
                print("Testing logout...")
                
                # Look for logout link in navbar
                logout_link = page.locator('a:has-text("Logout")')
                if logout_link.is_visible():
                    logout_link.click()
                    page.wait_for_load_state("networkidle")
                    
                    logout_url = page.url
                    print(f"   URL after logout: {logout_url}")
                    
                    if "login" in logout_url:
                        print("Logout successful! Redirected to login page")
                    else:
                        print("Logout may not have worked as expected")
                else:
                    print("Logout link not found")
                
            else:
                print("Login failed! Still on login page")
                
                # Check for error messages
                try:
                    error_message = page.locator('.alert-danger').text_content()
                    print(f"   Error message: {error_message}")
                except:
                    print("   No error message found")
            
            # Test password toggle
            print("Testing password toggle...")
            page.goto("http://localhost:8000/accounts/login/")
            
            password_field = page.locator('input[name="password"]')
            password_field.fill("testpassword")
            
            # Check initial state
            password_type = password_field.get_attribute('type')
            print(f"   Initial password type: {password_type}")
            
            # Click toggle button
            toggle_button = page.locator('.password-toggle')
            if toggle_button.is_visible():
                toggle_button.click()
                
                # Check if password is now visible
                password_type = password_field.get_attribute('type')
                print(f"   Password type after toggle: {password_type}")
                
                if password_type == 'text':
                    print("Password toggle works!")
                else:
                    print("Password toggle failed")
            else:
                print("Password toggle button not found")
            
            print("\nTest completed!")
            
        except Exception as e:
            print(f"Test failed with error: {str(e).encode('ascii', 'ignore').decode('ascii')}")
            raise
        
        finally:
            browser.close()


def main():
    """Main function to run the test"""
    print("Starting Simple Login Test")
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
    test_login_functionality()


if __name__ == "__main__":
    main()
