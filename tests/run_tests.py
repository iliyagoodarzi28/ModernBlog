#!/usr/bin/env python
"""
Simple test runner for Playwright login tests
Run this script to execute all login tests
"""

import os
import sys
import subprocess
import django
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def install_playwright():
    """Install Playwright and browsers if not already installed"""
    try:
        import playwright
        print("✓ Playwright is already installed")
    except ImportError:
        print("Installing Playwright...")
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright", "pytest-playwright"], check=True)
        print("✓ Playwright installed")
    
    # Install browsers
    print("Installing Playwright browsers...")
    subprocess.run([sys.executable, "-m", "playwright", "install"], check=True)
    print("✓ Playwright browsers installed")

def run_tests():
    """Run the Playwright tests"""
    print("Starting Django development server...")
    
    # Start Django server in background
    server_process = subprocess.Popen([
        sys.executable, "manage.py", "runserver", "8000"
    ], cwd=project_root)
    
    try:
        # Wait a moment for server to start
        import time
        time.sleep(3)
        
        print("Running Playwright tests...")
        
        # Run tests
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_login.py", 
            "-v", 
            "--tb=short"
        ], cwd=project_root)
        
        return result.returncode == 0
        
    finally:
        # Stop the server
        server_process.terminate()
        server_process.wait()
        print("Django server stopped")

def main():
    """Main function"""
    print("🚀 Starting Playwright Login Tests")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not (project_root / "manage.py").exists():
        print("❌ Error: manage.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Install Playwright if needed
    install_playwright()
    
    # Run tests
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
