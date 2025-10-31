# Playwright Tests for Django Login Functionality

This directory contains comprehensive Playwright tests for testing the Django login functionality in the accounts app.

## Files

- `test_login.py` - Comprehensive test suite with pytest
- `simple_login_test.py` - Simple standalone test that can be run immediately
- `conftest.py` - pytest configuration
- `requirements.txt` - Required packages for testing
- `run_tests.py` - Test runner script

## Quick Start

### 1. Install Playwright

```bash
pip install playwright pytest-playwright
playwright install
```

### 2. Start Django Server

```bash
python manage.py runserver
```

### 3. Run Simple Test

```bash
python tests/simple_login_test.py
```

### 4. Run Full Test Suite

```bash
python tests/run_tests.py
```

## Test Coverage

The tests cover:

### Basic Functionality
- ✅ Login page loads correctly
- ✅ Form elements are visible and functional
- ✅ Successful login with valid credentials
- ✅ Failed login with invalid credentials
- ✅ Form validation
- ✅ Password visibility toggle
- ✅ Remember me functionality

### User Experience
- ✅ Responsive design on different screen sizes
- ✅ Accessibility features
- ✅ Navigation links
- ✅ Error handling and messages
- ✅ Success messages

### Security
- ✅ CSRF protection
- ✅ Authentication requirements for protected pages
- ✅ Session management

### API Endpoints
- ✅ User stats API requires authentication
- ✅ User activities API requires authentication

## Test Data

The tests automatically create a test user with:
- Email: `test@example.com`
- Username: `testuser`
- Password: `TestPassword123!`
- Full Name: `Test User`

## Configuration

### Browser Settings
- Default browser: Chromium
- Viewport: 1280x720
- Headless mode can be enabled by setting `headless=True`

### Django Settings
- Server URL: `http://localhost:8000`
- Login URL: `/accounts/login/`
- Home URL: `/`

## Running Tests

### Individual Test
```bash
python -m pytest tests/test_login.py::TestLoginFunctionality::test_successful_login_with_valid_credentials -v
```

### All Login Tests
```bash
python -m pytest tests/test_login.py -v
```

### With Coverage
```bash
python -m pytest tests/test_login.py --cov=accounts --cov-report=html
```

## Troubleshooting

### Common Issues

1. **Django server not running**
   - Start server: `python manage.py runserver`

2. **Playwright not installed**
   - Install: `pip install playwright`
   - Install browsers: `playwright install`

3. **Test user doesn't exist**
   - Tests automatically create test user
   - Or create manually: `python manage.py shell` then create user

4. **CSRF errors**
   - Make sure CSRF middleware is enabled
   - Check that forms include `{% csrf_token %}`

### Debug Mode

To run tests in debug mode (non-headless):
```python
browser = p.chromium.launch(headless=False)
```

## Test Results

Successful test run should show:
- ✅ Page loads correctly
- ✅ Form elements are visible
- ✅ Login works with valid credentials
- ✅ Login fails with invalid credentials
- ✅ Password toggle works
- ✅ Logout works
- ✅ Redirects work correctly

## Contributing

When adding new tests:
1. Follow the existing naming conventions
2. Add proper docstrings
3. Include both positive and negative test cases
4. Test edge cases and error conditions
5. Update this README if adding new test categories
