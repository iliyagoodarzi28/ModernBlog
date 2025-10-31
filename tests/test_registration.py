"""
Comprehensive Playwright test for Django registration functionality
Tests the accounts/register/ endpoint with various scenarios
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


def test_registration_functionality():
    """Test registration functionality comprehensively"""
    
    # Start Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            print("Testing Registration Functionality")
            print("=" * 50)
            
            # Step 1: Navigate to registration page
            print("Step 1: Navigating to registration page...")
            page.goto("http://localhost:8000/accounts/register/")
            
            # Check if page loaded correctly
            title = page.title()
            print(f"   Page title: {title}")
            
            # Check main heading
            heading = page.locator("h2").text_content()
            print(f"   Main heading: {heading}")
            
            # Step 2: Test form elements
            print("\nStep 2: Checking form elements...")
            
            # Check required fields
            username_field = page.locator('input[name="username"]')
            email_field = page.locator('input[name="email"]')
            password1_field = page.locator('input[name="password1"]')
            password2_field = page.locator('input[name="password2"]')
            submit_button = page.locator('button[type="submit"]').first
            
            print(f"   Username field visible: {username_field.is_visible()}")
            print(f"   Email field visible: {email_field.is_visible()}")
            print(f"   Password1 field visible: {password1_field.is_visible()}")
            print(f"   Password2 field visible: {password2_field.is_visible()}")
            print(f"   Submit button visible: {submit_button.is_visible()}")
            
            # Step 3: Test successful registration
            print("\nStep 3: Testing successful registration...")
            
            # Generate unique test data
            import random
            test_id = random.randint(1000, 9999)
            test_email = f"testuser{test_id}@example.com"
            test_username = f"testuser{test_id}"
            test_password = "TestPassword123!"
            
            print(f"   Test email: {test_email}")
            print(f"   Test username: {test_username}")
            
            # Fill registration form
            username_field.fill(test_username)
            email_field.fill(test_email)
            password1_field.fill(test_password)
            password2_field.fill(test_password)
            
            # Check terms and conditions checkbox
            terms_checkbox = page.locator('input[name="terms_accepted"]')
            if terms_checkbox.is_visible():
                terms_checkbox.check()
                print("   Terms checkbox checked")
            
            # Submit form
            submit_button.click()
            
            # Wait for registration to complete
            page.wait_for_load_state("networkidle")
            
            # Check registration result
            current_url = page.url
            print(f"   After registration URL: {current_url}")
            
            if "profile" in current_url or "accounts/profile" in current_url:
                print("   SUCCESS: Registration successful! Redirected to profile page")
                
                # Check for success message
                try:
                    success_message = page.locator('.alert-success').text_content()
                    print(f"   Success message: {success_message}")
                except:
                    print("   No success message found")
                
                # Check if user is logged in
                user_button = page.locator('button:has-text("' + test_username + '")')
                if user_button.is_visible():
                    print("   SUCCESS: User is logged in automatically")
                else:
                    print("   INFO: User login status unclear")
                    
            else:
                print("   ERROR: Registration failed! Still on registration page")
                
                # Check for error messages
                try:
                    error_message = page.locator('.alert-danger').text_content()
                    print(f"   Error message: {error_message}")
                except:
                    print("   No error message found")
            
            # Step 4: Test form validation
            print("\nStep 4: Testing form validation...")
            
            # Navigate back to registration page
            page.goto("http://localhost:8000/accounts/register/")
            
            # Test empty form submission
            print("   Testing empty form submission...")
            submit_button = page.locator('button[type="submit"]').first
            submit_button.click()
            page.wait_for_load_state("networkidle")
            
            # Check for validation errors
            validation_errors = page.locator('.invalid-feedback')
            if validation_errors.count() > 0:
                print(f"   SUCCESS: {validation_errors.count()} validation errors found")
            else:
                print("   INFO: No validation errors found")
            
            # Step 5: Test duplicate email
            print("\nStep 5: Testing duplicate email validation...")
            
            # Try to register with existing email
            username_field = page.locator('input[name="username"]')
            email_field = page.locator('input[name="email"]')
            password1_field = page.locator('input[name="password1"]')
            password2_field = page.locator('input[name="password2"]')
            
            username_field.fill("newuser123")
            email_field.fill("test@example.com")  # This email already exists
            password1_field.fill("TestPassword123!")
            password2_field.fill("TestPassword123!")
            
            terms_checkbox = page.locator('input[name="terms_accepted"]')
            if terms_checkbox.is_visible():
                terms_checkbox.check()
            
            submit_button.click()
            page.wait_for_load_state("networkidle")
            
            # Check for duplicate email error
            try:
                error_message = page.locator('.alert-danger').text_content()
                if "email" in error_message.lower():
                    print("   SUCCESS: Duplicate email validation working")
                else:
                    print(f"   INFO: Error message: {error_message}")
            except:
                print("   INFO: No error message found")
            
            # Step 6: Test password mismatch
            print("\nStep 6: Testing password mismatch validation...")
            
            page.goto("http://localhost:8000/accounts/register/")
            
            username_field = page.locator('input[name="username"]')
            email_field = page.locator('input[name="email"]')
            password1_field = page.locator('input[name="password1"]')
            password2_field = page.locator('input[name="password2"]')
            
            username_field.fill("newuser456")
            email_field.fill("newuser456@example.com")
            password1_field.fill("TestPassword123!")
            password2_field.fill("DifferentPassword123!")  # Mismatched passwords
            
            terms_checkbox = page.locator('input[name="terms_accepted"]')
            if terms_checkbox.is_visible():
                terms_checkbox.check()
            
            submit_button.click()
            page.wait_for_load_state("networkidle")
            
            # Check for password mismatch error
            try:
                error_message = page.locator('.alert-danger').text_content()
                if "password" in error_message.lower() or "match" in error_message.lower():
                    print("   SUCCESS: Password mismatch validation working")
                else:
                    print(f"   INFO: Error message: {error_message}")
            except:
                print("   INFO: No error message found")
            
            # Step 7: Test optional fields
            print("\nStep 7: Testing optional fields...")
            
            page.goto("http://localhost:8000/accounts/register/")
            
            # Check for optional fields
            full_name_field = page.locator('input[name="full_name"]')
            phone_field = page.locator('input[name="phone"]')
            gender_field = page.locator('select[name="gender"]')
            birth_date_field = page.locator('input[name="birth_date"]')
            
            print(f"   Full name field visible: {full_name_field.is_visible()}")
            print(f"   Phone field visible: {phone_field.is_visible()}")
            print(f"   Gender field visible: {gender_field.is_visible()}")
            print(f"   Birth date field visible: {birth_date_field.is_visible()}")
            
            # Test registration with optional fields filled
            username_field = page.locator('input[name="username"]')
            email_field = page.locator('input[name="email"]')
            password1_field = page.locator('input[name="password1"]')
            password2_field = page.locator('input[name="password2"]')
            
            test_id = random.randint(1000, 9999)
            username_field.fill(f"fulluser{test_id}")
            email_field.fill(f"fulluser{test_id}@example.com")
            password1_field.fill("TestPassword123!")
            password2_field.fill("TestPassword123!")
            
            # Fill optional fields
            if full_name_field.is_visible():
                full_name_field.fill("Test User Full Name")
            if phone_field.is_visible():
                phone_field.fill("09123456789")
            if gender_field.is_visible():
                gender_field.select_option("M")
            if birth_date_field.is_visible():
                birth_date_field.fill("1990-01-01")
            
            terms_checkbox = page.locator('input[name="terms_accepted"]')
            if terms_checkbox.is_visible():
                terms_checkbox.check()
            
            submit_button.click()
            page.wait_for_load_state("networkidle")
            
            current_url = page.url
            if "profile" in current_url:
                print("   SUCCESS: Registration with optional fields successful")
            else:
                print("   INFO: Registration with optional fields may have failed")
            
            print("\nRegistration Test Completed!")
            
        except Exception as e:
            print(f"Test failed with error: {str(e).encode('ascii', 'ignore').decode('ascii')}")
            raise
        
        finally:
            browser.close()


def main():
    """Main function to run the registration test"""
    print("Starting Registration Functionality Test")
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
    test_registration_functionality()


if __name__ == "__main__":
    main()
