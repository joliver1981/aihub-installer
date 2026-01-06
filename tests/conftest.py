"""
Playwright Test Configuration for AI Hub
=========================================

This file contains shared fixtures and configuration used across all e2e tests.

Usage:
    1. Start your Flask application: python app.py
    2. Run tests: pytest tests/e2e/ -v
    3. Run with visible browser: pytest tests/e2e/ -v --headed
    4. Run specific test: pytest tests/e2e/test_smoke.py -v --headed
"""

import pytest
from playwright.sync_api import Page, BrowserContext, expect
from typing import Generator
import os

# =============================================================================
# CONFIGURATION
# =============================================================================

# Base URL for your application - adjust if running on different port
BASE_URL = "http://10.0.0.7:5001"  #os.environ.get("TEST_BASE_URL", "http://10.0.0.7:5001")

# Test user credentials - these should match a user in your database
# For production testing, create a dedicated test user
TEST_USER_EMAIL = os.environ.get("TEST_USER_EMAIL", "admin")
TEST_USER_PASSWORD = os.environ.get("TEST_USER_PASSWORD", "admin")

# Timeouts (in milliseconds)
DEFAULT_TIMEOUT = 30000  # 30 seconds for page loads
NAVIGATION_TIMEOUT = 15000  # 15 seconds for navigation


# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================

def pytest_configure(config):
    """Add custom markers for test categorization."""
    config.addinivalue_line("markers", "smoke: Quick smoke tests for basic functionality")
    config.addinivalue_line("markers", "auth: Tests that require authentication")
    config.addinivalue_line("markers", "slow: Tests that take longer to run")


# =============================================================================
# BROWSER CONFIGURATION FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context settings for all tests."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 800},
        "ignore_https_errors": True,  # Useful for local dev with self-signed certs
    }


# Note: We use the built-in base_url fixture from pytest-playwright
# Configure it in pytest.ini or via command line: pytest --base-url http://localhost:5000


# =============================================================================
# AUTHENTICATION FIXTURES
# =============================================================================

@pytest.fixture
def login_page(page: Page, base_url: str) -> Page:
    """Navigate to the login page."""
    page.goto(f"{base_url}/login", timeout=NAVIGATION_TIMEOUT)
    page.wait_for_load_state("networkidle")
    return page


@pytest.fixture
def logged_in_page(page: Page, base_url: str) -> Generator[Page, None, None]:
    """
    Provides a page with an authenticated user session.
    
    This fixture:
    1. Navigates to the login page
    2. Fills in credentials
    3. Submits the form
    4. Waits for successful redirect to dashboard
    5. Returns the authenticated page for use in tests
    
    Usage in tests:
        def test_something(logged_in_page, base_url):
            logged_in_page.goto(f"{base_url}/some-protected-page")
            # ... rest of test
    """
    # Use the base_url from pytest-playwright (configured in pytest.ini)
    url = base_url if base_url else BASE_URL
    
    # Navigate to login
    page.goto(f"{url}/login", timeout=NAVIGATION_TIMEOUT)
    page.wait_for_load_state("networkidle")
    
    # Check if we're already logged in (redirected to home)
    if "/login" not in page.url:
        yield page
        return
    
    # Fill in login form
    # Using multiple selector strategies to be resilient to HTML changes
    username_field = page.locator('input[name="username"], input[name="email"], #username, #email').first
    password_field = page.locator('input[name="password"], input[type="password"], #password').first
    
    username_field.fill(TEST_USER_EMAIL)
    password_field.fill(TEST_USER_PASSWORD)
    
    # Submit the form
    submit_button = page.locator('button[type="submit"], input[type="submit"], .btn-login').first
    submit_button.click()
    
    # Wait for navigation away from login page
    page.wait_for_url(lambda url: "/login" not in url, timeout=DEFAULT_TIMEOUT)
    page.wait_for_load_state("networkidle")
    
    yield page


# =============================================================================
# UTILITY FIXTURES
# =============================================================================

@pytest.fixture
def screenshot_on_failure(page: Page, request):
    """
    Automatically capture a screenshot when a test fails.
    Screenshots are saved to: tests/screenshots/
    """
    yield
    
    # Check if the test failed
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        # Create screenshots directory if it doesn't exist
        screenshot_dir = os.path.join(os.path.dirname(__file__), "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        
        # Generate filename from test name
        test_name = request.node.name.replace("/", "_").replace(":", "_")
        screenshot_path = os.path.join(screenshot_dir, f"{test_name}.png")
        
        # Capture screenshot
        page.screenshot(path=screenshot_path)
        print(f"\nScreenshot saved: {screenshot_path}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to make test result available to fixtures."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


# =============================================================================
# PAGE OBJECT HELPERS
# =============================================================================

class DashboardPage:
    """Page object for the AI Hub Dashboard."""
    
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        
        # Define locators for key elements
        self.welcome_heading = page.locator(".welcome-section h1, .welcome-free h1")
        self.new_chat_button = page.locator('a:has-text("New Chat"), a:has-text("Chat with AI")')
        self.create_agent_button = page.locator('a:has-text("Create Agent"), a:has-text("Manage Agents")')
        self.quick_actions_section = page.locator(".action-grid")
        self.sidebar = page.locator(".new-sidebar, #newSidebar")
    
    def navigate(self):
        """Navigate to the dashboard."""
        self.page.goto(f"{self.base_url}/", timeout=NAVIGATION_TIMEOUT)
        self.page.wait_for_load_state("networkidle")
        return self
    
    def get_welcome_text(self) -> str:
        """Get the welcome message text."""
        return self.welcome_heading.text_content()
    
    def click_new_chat(self):
        """Click the New Chat button."""
        self.new_chat_button.first.click()
        self.page.wait_for_load_state("networkidle")
    
    def click_create_agent(self):
        """Click the Create Agent button."""
        self.create_agent_button.first.click()
        self.page.wait_for_load_state("networkidle")
    
    def is_sidebar_visible(self) -> bool:
        """Check if the sidebar is visible."""
        return self.sidebar.is_visible()


class AgentsPage:
    """Page object for the Agents/Assistants page."""
    
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
    
    def navigate(self):
        """Navigate to the agents page."""
        self.page.goto(f"{self.base_url}/assistants", timeout=NAVIGATION_TIMEOUT)
        self.page.wait_for_load_state("networkidle")
        return self


@pytest.fixture
def dashboard_page(logged_in_page: Page, base_url: str) -> DashboardPage:
    """Provides a DashboardPage object for testing the dashboard."""
    return DashboardPage(logged_in_page, base_url)


@pytest.fixture
def agents_page(logged_in_page: Page, base_url: str) -> AgentsPage:
    """Provides an AgentsPage object for testing the agents functionality."""
    return AgentsPage(logged_in_page, base_url)
