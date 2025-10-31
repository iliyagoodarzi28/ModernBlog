# Playwright configuration for Django login tests
import os
import pytest
from playwright.sync_api import sync_playwright
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()


@pytest.fixture(scope="session")
def browser_context_args():
    """Configure browser context for tests"""
    return {
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="session")
def playwright_context():
    """Setup Playwright context"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set to True for CI
        context = browser.new_context()
        yield context
        context.close()
        browser.close()


@pytest.fixture
def page(playwright_context):
    """Create a new page for each test"""
    page = playwright_context.new_page()
    yield page
    page.close()


# Test configuration
pytest_plugins = ["pytest_playwright"]
