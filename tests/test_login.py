"""
Comprehensive Playwright tests for Django login functionality
Tests the accounts/login/ endpoint with various scenarios
"""

import pytest
from playwright.sync_api import Page, expect
import os
import sys
import django
from django.conf import settings
from django.contrib.auth import get_user_model

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

User = get_user_model()


class TestLoginFunctionality:
    """Test class for login functionality"""

    @pytest.fixture(autouse=True)
    def setup_test_data(self):
        """Setup test data before each test"""
        # Create test user
        self.test_user_email = "test@example.com"
        self.test_user_password = "TestPassword123!"
        self.test_user_username = "testuser"
        
        # Create user if it doesn't exist
        if not User.objects.filter(email=self.test_user_email).exists():
            User.objects.create_user(
                email=self.test_user_email,
                username=self.test_user_username,
                password=self.test_user_password,
                full_name="Test User"
            )

    def test_login_page_loads_correctly(self, page: Page):
        """Test that the login page loads with all required elements"""
        page.goto("http://localhost:8000/accounts/login/")
        
        # Check page title
        expect(page).to_have_title("Sign In - ModernBlog")
        
        # Check main heading
        expect(page.locator("h2")).to_contain_text("Welcome Back")
        
        # Check form elements
        expect(page.locator('input[name="username"]')).to_be_visible()
        expect(page.locator('input[name="password"]')).to_be_visible()
        expect(page.locator('button[type="submit"]')).to_be_visible()
        
        # Check remember me checkbox
        expect(page.locator('input[name="remember_me"]')).to_be_visible()
        
        # Check social login buttons
        expect(page.locator('button:has-text("Google")')).to_be_visible()
        expect(page.locator('button:has-text("Facebook")')).to_be_visible()
        
        # Check sign up link
        expect(page.locator('a:has-text("Sign up here")')).to_be_visible()

    def test_successful_login_with_valid_credentials(self, page: Page):
        """Test successful login with valid credentials"""
        page.goto("http://localhost:8000/accounts/login/")
        
        # Fill login form
        page.fill('input[name="username"]', self.test_user_email)
        page.fill('input[name="password"]', self.test_user_password)
        
        # Submit form
        page.click('button[type="submit"]')
        
        # Should redirect to home page
        expect(page).to_have_url("http://localhost:8000/")
        
        # Check for success message
        expect(page.locator('.alert-success')).to_be_visible()

    def test_login_with_remember_me(self, page: Page):
        """Test login with remember me checkbox checked"""
        page.goto("http://localhost:8000/accounts/login/")
        
        # Fill login form
        page.fill('input[name="username"]', self.test_user_email)
        page.fill('input[name="password"]', self.test_user_password)
        
        # Check remember me
        page.check('input[name="remember_me"]')
        
        # Submit form
        page.click('button[type="submit"]')
        
        # Should redirect to home page
        expect(page).to_have_url("http://localhost:8000/")

    def test_login_with_invalid_email(self, page: Page):
        """Test login with invalid email format"""
        page.goto("http://localhost:8000/accounts/login/")
        
        # Fill form with invalid email
        page.fill('input[name="username"]', "invalid-email")
        page.fill('input[name="password"]', self.test_user_password)
        
        # Submit form
        page.click('button[type="submit"]')
        
        # Should stay on login page
        expect(page).to_have_url("http://localhost:8000/accounts/login/")
        
        # Check for error message
        expect(page.locator('.alert-danger')).to_be_visible()

    def test_login_with_wrong_password(self, page: Page):
        """Test login with wrong password"""
        page.goto("http://localhost:8000/accounts/login/")
        
        # Fill form with wrong password
        page.fill('input[name="username"]', self.test_user_email)
        page.fill('input[name="password"]', "wrongpassword")
        
        # Submit form
        page.click('button[type="submit"]')
        
        # Should stay on login page
        expect(page).to_have_url("http://localhost:8000/accounts/login/")
        
        # Check for error message
        expect(page.locator('.alert-danger')).to_be_visible()

    def test_login_with_empty_fields(self, page: Page):
        """Test login with empty fields"""
        page.goto("http://localhost:8000/accounts/login/")
        
        # Submit form without filling fields
        page.click('button[type="submit"]')
        
        # Should stay on login page
        expect(page).to_have_url("http://localhost:8000/accounts/login/")
        
        # Check for validation errors
        expect(page.locator('.invalid-feedback')).to_be_visible()

    def test_password_toggle_functionality(self, page: Page):
        """Test password visibility toggle"""
        page.goto("http://localhost:8000/accounts/login/")
        
        # Fill password field
        page.fill('input[name="password"]', self.test_user_password)
        
        # Check initial state (password should be hidden)
        password_input = page.locator('input[name="password"]')
        expect(password_input).to_have_attribute('type', 'password')
        
        # Click toggle button
        page.click('.password-toggle')
        
        # Password should be visible
        expect(password_input).to_have_attribute('type', 'text')
        
        # Click toggle again
        page.click('.password-toggle')
        
        # Password should be hidden again
        expect(password_input).to_have_attribute('type', 'password')

    def test_form_validation_styling(self, page: Page):
        """Test form validation styling on blur/input"""
        page.goto("http://localhost:8000/accounts/login/")
        
        # Focus and blur email field
        email_input = page.locator('input[name="username"]')
        email_input.focus()
        email_input.blur()
        
        # Should show invalid styling
        expect(email_input).to_have_class(/is-invalid/)
        
        # Type valid email
        email_input.fill(self.test_user_email)
        
        # Should show valid styling
        expect(email_input).to_have_class(/is-valid/)

    def test_redirect_after_login(self, page: Page):
        """Test redirect to intended page after login"""
        # Try to access protected page first
        page.goto("http://localhost:8000/accounts/profile/")
        
        # Should redirect to login page
        expect(page).to_have_url("http://localhost:8000/accounts/login/")
        
        # Login
        page.fill('input[name="username"]', self.test_user_email)
        page.fill('input[name="password"]', self.test_user_password)
        page.click('button[type="submit"]')
        
        # Should redirect back to profile page
        expect(page).to_have_url("http://localhost:8000/accounts/profile/")

    def test_logout_functionality(self, page: Page):
        """Test logout functionality"""
        # Login first
        page.goto("http://localhost:8000/accounts/login/")
        page.fill('input[name="username"]', self.test_user_email)
        page.fill('input[name="password"]', self.test_user_password)
        page.click('button[type="submit"]')
        
        # Should be on home page
        expect(page).to_have_url("http://localhost:8000/")
        
        # Look for logout link/button (assuming it exists in navbar)
        logout_link = page.locator('a:has-text("Logout")')
        if logout_link.is_visible():
            logout_link.click()
            
            # Should redirect to login page
            expect(page).to_have_url("http://localhost:8000/accounts/login/")

    def test_social_login_buttons_present(self, page: Page):
        """Test that social login buttons are present and clickable"""
        page.goto("http://localhost:8000/accounts/login/")
        
        # Check Google button
        google_button = page.locator('button:has-text("Google")')
        expect(google_button).to_be_visible()
        expect(google_button).to_be_enabled()
        
        # Check Facebook button
        facebook_button = page.locator('button:has-text("Facebook")')
        expect(facebook_button).to_be_visible()
        expect(facebook_button).to_be_enabled()

    def test_responsive_design(self, page: Page):
        """Test responsive design on different screen sizes"""
        # Test mobile view
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto("http://localhost:8000/accounts/login/")
        
        # Check that form is still visible and usable
        expect(page.locator('input[name="username"]')).to_be_visible()
        expect(page.locator('input[name="password"]')).to_be_visible()
        expect(page.locator('button[type="submit"]')).to_be_visible()
        
        # Test tablet view
        page.set_viewport_size({"width": 768, "height": 1024})
        page.goto("http://localhost:8000/accounts/login/")
        
        # Check that form is still visible and usable
        expect(page.locator('input[name="username"]')).to_be_visible()
        expect(page.locator('input[name="password"]')).to_be_visible()
        expect(page.locator('button[type="submit"]')).to_be_visible()

    def test_csrf_protection(self, page: Page):
        """Test CSRF protection is working"""
        page.goto("http://localhost:8000/accounts/login/")
        
        # Check that CSRF token is present
        csrf_token = page.locator('input[name="csrfmiddlewaretoken"]')
        expect(csrf_token).to_be_visible()
        expect(csrf_token).to_have_attribute('value')

    def test_accessibility_features(self, page: Page):
        """Test accessibility features"""
        page.goto("http://localhost:8000/accounts/login/")
        
        # Check for proper labels
        username_label = page.locator('label[for="id_username"]')
        password_label = page.locator('label[for="id_password"]')
        
        expect(username_label).to_be_visible()
        expect(password_label).to_be_visible()
        
        # Check for proper form structure
        form = page.locator('form')
        expect(form).to_be_visible()
        
        # Check for proper button type
        submit_button = page.locator('button[type="submit"]')
        expect(submit_button).to_be_visible()

    def test_navigation_links(self, page: Page):
        """Test navigation links on login page"""
        page.goto("http://localhost:8000/accounts/login/")
        
        # Test sign up link
        signup_link = page.locator('a:has-text("Sign up here")')
        expect(signup_link).to_be_visible()
        signup_link.click()
        expect(page).to_have_url("http://localhost:8000/accounts/register/")
        
        # Go back to login
        page.goto("http://localhost:8000/accounts/login/")
        
        # Test back to home link
        home_link = page.locator('a:has-text("Back to Home")')
        expect(home_link).to_be_visible()
        home_link.click()
        expect(page).to_have_url("http://localhost:8000/")


class TestLoginAPI:
    """Test class for login-related API endpoints"""

    def test_user_stats_api_requires_login(self, page: Page):
        """Test that user stats API requires authentication"""
        response = page.request.get("http://localhost:8000/accounts/api/stats/")
        expect(response).to_have_status(302)  # Redirect to login

    def test_user_activities_api_requires_login(self, page: Page):
        """Test that user activities API requires authentication"""
        response = page.request.get("http://localhost:8000/accounts/api/activities/")
        expect(response).to_have_status(302)  # Redirect to login


if __name__ == "__main__":
    # Run tests with: python -m pytest tests/test_login.py -v
    pytest.main([__file__, "-v"])
