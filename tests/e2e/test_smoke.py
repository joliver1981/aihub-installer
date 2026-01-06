"""
Smoke Tests for AI Hub
======================

These tests verify that core pages load correctly and key elements are present.
Run these first to ensure the application is functioning at a basic level.

Usage:
    pytest tests/e2e/test_smoke.py -v
    pytest tests/e2e/test_smoke.py -v --headed  # Watch tests run
    pytest tests/e2e/test_smoke.py -v -k "login"  # Run only login tests
"""

import pytest
import re
from playwright.sync_api import Page, expect


class TestPublicPages:
    """Tests for pages that don't require authentication."""
    
    @pytest.mark.smoke
    def test_login_page_loads(self, page: Page, base_url: str):
        """Verify the login page loads and has required elements."""
        # Navigate to login page
        page.goto(f"{base_url}/login")
        page.wait_for_load_state("networkidle")
        
        # Verify we're on the login page (not redirected)
        # If already logged in, this might redirect - that's okay
        if "/login" in page.url:
            # Check for login form elements
            expect(page.locator('input[name="username"], input[name="email"], #username, #email')).to_be_visible()
            expect(page.locator('input[type="password"]')).to_be_visible()
            expect(page.locator('button[type="submit"], input[type="submit"]')).to_be_visible()
    
    @pytest.mark.smoke
    def test_login_page_title(self, page: Page, base_url: str):
        """Verify the login page has an appropriate title."""
        page.goto(f"{base_url}/login")
        
        # Title should be "Login" (or contain it)
        # Use re.compile for case-insensitive regex matching
        expect(page).to_have_title(re.compile(r"ai hub", re.IGNORECASE))


class TestAuthentication:
    """Tests for the authentication flow."""
    
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_successful_login_redirects_to_dashboard(self, logged_in_page: Page, base_url: str):
        """Verify successful login redirects to the dashboard/home page."""
        # The logged_in_page fixture handles the login
        # We just need to verify we ended up in the right place
        
        # Should not be on the login page anymore
        assert "/login" not in logged_in_page.url
        
        # Should see dashboard elements
        # Using flexible selectors since dashboard layout may vary
        dashboard_indicators = logged_in_page.locator(
            ".dashboard-container, "
            ".welcome-section, "
            ".welcome-free, "
            "h1:has-text('Welcome'), "
            ".new-sidebar"
        )
        expect(dashboard_indicators.first).to_be_visible()
    
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_sidebar_navigation_visible(self, logged_in_page: Page):
        """Verify the sidebar navigation is visible after login."""
        sidebar = logged_in_page.locator(".new-sidebar, #newSidebar")
        expect(sidebar).to_be_visible()
    
    @pytest.mark.smoke  
    @pytest.mark.auth
    def test_user_is_logged_in(self, logged_in_page: Page):
        """Verify user appears to be logged in (user menu visible, etc.)."""
        # Look for indicators that user is logged in
        user_indicators = logged_in_page.locator(
            ".new-user-dropdown, "
            ".user-menu, "
            ".tier-info-badge, "
            ".user-avatar, "
            "a[href*='logout']"
        )
        expect(user_indicators.first).to_be_visible()


class TestDashboard:
    """Tests for the main dashboard page."""
    
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_dashboard_loads_successfully(self, logged_in_page: Page, base_url: str):
        """Verify the dashboard loads without errors."""
        # Navigate explicitly to home/dashboard
        logged_in_page.goto(f"{base_url}/")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Check for dashboard container
        dashboard = logged_in_page.locator(".dashboard-container")
        expect(dashboard).to_be_visible()
    
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_dashboard_has_welcome_message(self, logged_in_page: Page, base_url: str):
        """Verify the dashboard shows a welcome message."""
        logged_in_page.goto(f"{base_url}/")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Look for welcome heading
        welcome = logged_in_page.locator("h1:has-text('Welcome')")
        expect(welcome).to_be_visible()
    
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_dashboard_has_quick_actions(self, logged_in_page: Page, base_url: str):
        """Verify the dashboard shows quick action cards."""
        logged_in_page.goto(f"{base_url}/")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Look for action grid or action cards
        actions = logged_in_page.locator(".action-grid, .action-card")
        expect(actions.first).to_be_visible()
    
    @pytest.mark.auth
    def test_chat_with_ai_action_works(self, logged_in_page: Page, base_url: str):
        """Verify clicking 'Chat with AI' navigates to the assistants page."""
        logged_in_page.goto(f"{base_url}/")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Find the action card in the dashboard (not sidebar links)
        # Target specifically the action-card with "Chat with AI" text
        chat_link = logged_in_page.locator('.action-grid a.action-card:has-text("Chat with AI")')
        
        expect(chat_link).to_be_visible()
        chat_link.click()
        
        # Wait for navigation to complete
        logged_in_page.wait_for_load_state("networkidle")
        
        # Verify we're on the assistants page
        expect(logged_in_page).to_have_url(re.compile(r"assistants"))
        
        # Verify key chat elements are present (from assistants.html)
        expect(logged_in_page.locator("#user-input")).to_be_visible()
        expect(logged_in_page.locator("#agent-dropdown")).to_be_visible()
        expect(logged_in_page.locator('button[onclick="sendMessage()"]')).to_be_visible()


class TestCoreNavigation:
    """Tests for core navigation elements and page access."""
    
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_agents_page_accessible(self, logged_in_page: Page, base_url: str):
        """Verify the agents/assistants page is accessible."""
        logged_in_page.goto(f"{base_url}/assistants")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Should not get a 404 or error page
        assert "404" not in logged_in_page.title().lower()
        assert "error" not in logged_in_page.title().lower()
        
        # Page should have loaded successfully
        expect(logged_in_page.locator("body")).to_be_visible()
    
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_jobs_page_accessible(self, logged_in_page: Page, base_url: str):
        """Verify the jobs page is accessible."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Should not get a 404
        assert "404" not in logged_in_page.title().lower()
    
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_sidebar_navigation_links_work(self, logged_in_page: Page, base_url: str):
        """Verify clicking sidebar links navigates correctly."""
        logged_in_page.goto(f"{base_url}/")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Click on Dashboard link in sidebar
        dashboard_link = logged_in_page.locator('.new-nav-link:has-text("Dashboard")').first
        dashboard_link.click()
        logged_in_page.wait_for_load_state("networkidle")
        
        # Should still be on home/dashboard
        # The URL should be root or /home
        current_path = logged_in_page.url.replace(base_url, "")
        assert current_path in ["/", "", "/home", "/dashboard"]


class TestResponsiveElements:
    """Tests for responsive/interactive UI elements."""
    
    @pytest.mark.auth
    def test_sidebar_toggle_works(self, logged_in_page: Page, base_url: str):
        """Verify the sidebar can be collapsed/expanded."""
        logged_in_page.goto(f"{base_url}/")
        logged_in_page.wait_for_load_state("networkidle")
        
        sidebar = logged_in_page.locator(".new-sidebar, #newSidebar")
        toggle_button = logged_in_page.locator(".new-sidebar-toggle")
        
        # Sidebar should start expanded (not collapsed)
        initial_has_collapsed = "collapsed" in (sidebar.get_attribute("class") or "")
        
        # Click toggle if visible
        if toggle_button.is_visible():
            toggle_button.click()
            logged_in_page.wait_for_timeout(500)  # Wait for animation
            
            # Class should have changed
            final_has_collapsed = "collapsed" in (sidebar.get_attribute("class") or "")
            assert initial_has_collapsed != final_has_collapsed
    
    @pytest.mark.auth
    def test_dropdown_menus_work(self, logged_in_page: Page, base_url: str):
        """Verify dropdown menus in sidebar expand when clicked."""
        logged_in_page.goto(f"{base_url}/")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Find a dropdown menu (like AI Agents)
        dropdown = logged_in_page.locator('.new-nav-dropdown:has-text("AI Agents")').first
        
        if dropdown.is_visible():
            dropdown.click()
            logged_in_page.wait_for_timeout(300)  # Wait for animation
            
            # Submenu should now be visible
            submenu = logged_in_page.locator("#agentsSubmenu")
            expect(submenu).to_have_class(re.compile(r"show"))


class TestPageLoadPerformance:
    """Basic performance checks for page loads."""
    
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_dashboard_loads_within_timeout(self, logged_in_page: Page, base_url: str):
        """Verify dashboard loads within acceptable time."""
        import time
        
        start = time.time()
        logged_in_page.goto(f"{base_url}/", timeout=10000)
        logged_in_page.wait_for_load_state("networkidle")
        elapsed = time.time() - start
        
        # Dashboard should load within 10 seconds
        assert elapsed < 10, f"Dashboard took {elapsed:.2f}s to load"
    
    @pytest.mark.auth
    def test_no_javascript_errors_on_dashboard(self, page: Page, logged_in_page: Page, base_url: str):
        """Verify no JavaScript errors occur on dashboard load."""
        errors = []
        
        # Listen for console errors
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        
        logged_in_page.goto(f"{base_url}/")
        logged_in_page.wait_for_load_state("networkidle")
        logged_in_page.wait_for_timeout(1000)  # Give time for any delayed errors
        
        # Filter out known acceptable errors (if any)
        critical_errors = [e for e in errors if "favicon" not in e.lower()]
        
        assert len(critical_errors) == 0, f"JavaScript errors found: {critical_errors}"
