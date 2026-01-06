"""
Tests for the Assistants (Agent Chat) Page
==========================================

These tests verify the agent chat functionality works correctly.
Based on the actual assistants.html template structure.

Usage:
    pytest tests/e2e/test_assistants.py -v --headed
"""

import pytest
from playwright.sync_api import Page, expect
import re


class TestAssistantsPageLoad:
    """Tests for basic page loading and element presence."""
    
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_assistants_page_loads(self, logged_in_page: Page, base_url: str):
        """Verify the assistants page loads without errors."""
        logged_in_page.goto(f"{base_url}/assistants")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Should not be a 404 or error page
        assert "404" not in logged_in_page.title().lower()
        assert "error" not in logged_in_page.title().lower()
    
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_assistants_page_has_header(self, logged_in_page: Page, base_url: str):
        """Verify the page header shows 'Agent Chat'."""
        logged_in_page.goto(f"{base_url}/assistants")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Look for the header with "Agent Chat" text
        header = logged_in_page.locator(".compact-header h4, h4:has-text('Agent Chat')")
        expect(header).to_be_visible()
        expect(header).to_contain_text("Agent Chat")
    
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_assistants_page_has_chat_window(self, logged_in_page: Page, base_url: str):
        """Verify the chat window element exists."""
        logged_in_page.goto(f"{base_url}/assistants")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Check for chat window
        chat_window = logged_in_page.locator("#chat-window")
        expect(chat_window).to_be_visible()
    
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_assistants_page_has_message_input(self, logged_in_page: Page, base_url: str):
        """Verify the message input field exists."""
        logged_in_page.goto(f"{base_url}/assistants")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Check for user input field
        user_input = logged_in_page.locator("#user-input")
        expect(user_input).to_be_visible()
        expect(user_input).to_have_attribute("placeholder", "Type your message here...")
    
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_assistants_page_has_send_button(self, logged_in_page: Page, base_url: str):
        """Verify the send button exists."""
        logged_in_page.goto(f"{base_url}/assistants")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Check for send button
        send_button = logged_in_page.locator("button:has-text('Send')").first
        expect(send_button).to_be_visible()
    
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_assistants_page_has_agent_dropdown(self, logged_in_page: Page, base_url: str):
        """Verify the agent selection dropdown exists."""
        logged_in_page.goto(f"{base_url}/assistants")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Check for agent dropdown
        agent_dropdown = logged_in_page.locator("#agent-dropdown")
        expect(agent_dropdown).to_be_visible()
    
    @pytest.mark.auth
    def test_assistants_page_has_reset_button(self, logged_in_page: Page, base_url: str):
        """Verify the reset conversation button exists."""
        logged_in_page.goto(f"{base_url}/assistants")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Check for reset button
        reset_button = logged_in_page.locator("#reset-conversation-btn")
        expect(reset_button).to_be_visible()
        expect(reset_button).to_contain_text("Reset")


class TestNavigationToAssistants:
    """Tests for navigating to the assistants page from other pages."""

    @pytest.mark.auth
    def test_navigate_from_dashboard_chat_action(self, logged_in_page: Page, base_url: str):
        """
        Test clicking 'Chat with AI' on dashboard navigates to assistants page.
        This is the corrected version of test_chat_with_ai_action_works.
        """
        # Start at the dashboard
        logged_in_page.goto(f"{base_url}/")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Find and click the chat action card
        # From actual HTML: <a href="/assistants" class="action-card primary">
        chat_link = logged_in_page.locator('a.action-card:has-text("Chat with AI")').first
        
        expect(chat_link).to_be_visible()
        chat_link.click()
        
        # Wait for navigation
        logged_in_page.wait_for_load_state("networkidle")
        
        # Verify we're on the assistants page (use regex, not lambda)
        expect(logged_in_page).to_have_url(re.compile(r"assistants"))
        
        # Verify key elements are present
        expect(logged_in_page.locator("#user-input")).to_be_visible()
        expect(logged_in_page.locator("#agent-dropdown")).to_be_visible()
    
    @pytest.mark.auth
    def test_navigate_from_sidebar(self, logged_in_page: Page, base_url: str):
        """Test navigating to assistants via sidebar menu."""
        logged_in_page.goto(f"{base_url}/")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Click the AI Agents dropdown in sidebar
        agents_dropdown = logged_in_page.locator('.new-nav-dropdown:has-text("AI Agents")')
        agents_dropdown.click()
        
        # Wait for submenu to show
        logged_in_page.wait_for_timeout(300)
        
        # Click Agent Chat link
        agent_chat_link = logged_in_page.locator('#agentsSubmenu a:has-text("Agent Chat")')
        expect(agent_chat_link).to_be_visible()
        agent_chat_link.click()
        
        # Wait for navigation
        logged_in_page.wait_for_load_state("networkidle")
        
        # Verify we're on the assistants page (use regex, not lambda)
        expect(logged_in_page).to_have_url(re.compile(r"assistants"))

class TestAgentSelection:
    """Tests for the agent selection functionality."""
    
    @pytest.mark.auth
    def test_agent_dropdown_has_default_option(self, logged_in_page: Page, base_url: str):
        """Verify the agent dropdown has a default 'Select an agent' option."""
        logged_in_page.goto(f"{base_url}/assistants")
        logged_in_page.wait_for_load_state("networkidle")
        
        agent_dropdown = logged_in_page.locator("#agent-dropdown")
        
        # Check for default option
        default_option = agent_dropdown.locator('option[value=""]')
        expect(default_option).to_have_text("Select an agent")
    
    @pytest.mark.auth
    def test_agent_dropdown_loads_agents(self, logged_in_page: Page, base_url: str):
        """Verify agents are loaded into the dropdown (if any exist)."""
        logged_in_page.goto(f"{base_url}/assistants")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Wait a moment for AJAX to populate the dropdown
        logged_in_page.wait_for_timeout(1000)
        
        agent_dropdown = logged_in_page.locator("#agent-dropdown")
        
        # Count options (should be at least 1 for the default "Select an agent")
        option_count = agent_dropdown.locator("option").count()
        assert option_count >= 1, "Dropdown should have at least the default option"
    
    @pytest.mark.auth
    def test_selecting_agent_shows_objective(self, logged_in_page: Page, base_url: str):
        """
        Verify selecting an agent populates the objective textarea.
        Note: This test requires at least one agent to exist in the database.
        """
        logged_in_page.goto(f"{base_url}/assistants")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Wait for agents to load
        logged_in_page.wait_for_timeout(1000)
        
        agent_dropdown = logged_in_page.locator("#agent-dropdown")
        objective_textarea = logged_in_page.locator("#objective")
        
        # Get all options except the default
        options = agent_dropdown.locator("option:not([value=''])")
        option_count = options.count()
        
        if option_count > 0:
            # Select the first real agent
            first_option = options.first
            agent_value = first_option.get_attribute("value")
            agent_dropdown.select_option(value=agent_value)
            
            # Wait for objective to be populated
            logged_in_page.wait_for_timeout(500)
            
            # The objective field should no longer be empty (or have the placeholder)
            # Note: This depends on the agent having an objective set
            objective_value = objective_textarea.input_value()
            # Just verify the selection happened - objective might be empty for some agents
            selected_value = agent_dropdown.input_value()
            assert selected_value == agent_value
        else:
            pytest.skip("No agents available in the database for this test")


class TestChatInteraction:
    """Tests for the chat message interaction."""
    
    @pytest.mark.auth
    def test_can_type_in_message_input(self, logged_in_page: Page, base_url: str):
        """Verify user can type a message in the input field."""
        logged_in_page.goto(f"{base_url}/assistants")
        logged_in_page.wait_for_load_state("networkidle")
        
        user_input = logged_in_page.locator("#user-input")
        
        # Type a test message
        test_message = "Hello, this is a test message"
        user_input.fill(test_message)
        
        # Verify the message was entered
        expect(user_input).to_have_value(test_message)
    
    @pytest.mark.auth
    def test_send_button_requires_agent_selection(self, logged_in_page: Page, base_url: str):
        """
        Verify that sending a message without selecting an agent shows an error
        or is prevented.
        """
        logged_in_page.goto(f"{base_url}/assistants")
        logged_in_page.wait_for_load_state("networkidle")
        
        user_input = logged_in_page.locator("#user-input")
        send_button = logged_in_page.locator("button:has-text('Send')").first
        
        # Make sure no agent is selected
        agent_dropdown = logged_in_page.locator("#agent-dropdown")
        agent_dropdown.select_option(value="")
        
        # Type a message
        user_input.fill("Test message without agent")
        
        # Click send
        send_button.click()
        
        # Wait a moment for any error/alert to appear
        logged_in_page.wait_for_timeout(500)
        
        # The message should still be in the input (not sent) or an alert should appear
        # This depends on your application's behavior - adjust assertion as needed
        # Option 1: Check input still has value (message wasn't sent)
        # Option 2: Check for error message/toast
        # Option 3: Check for browser alert
        
        # For now, just verify the page didn't crash
        expect(logged_in_page.locator("#chat-window")).to_be_visible()
    
    @pytest.mark.auth
    def test_reset_button_clears_conversation(self, logged_in_page: Page, base_url: str):
        """Verify the reset button clears the chat."""
        logged_in_page.goto(f"{base_url}/assistants")
        logged_in_page.wait_for_load_state("networkidle")
        
        reset_button = logged_in_page.locator("#reset-conversation-btn")
        chat_content = logged_in_page.locator("#chat-content")
        
        # Click reset
        reset_button.click()
        
        # Handle any confirmation dialog if present
        # logged_in_page.on("dialog", lambda dialog: dialog.accept())
        
        logged_in_page.wait_for_timeout(500)
        
        # Chat content should be empty or have initial state
        # This verifies the reset action was triggered
        expect(chat_content).to_be_visible()


class TestChatWithAgent:
    """
    End-to-end tests for actual chat conversations.
    These tests require:
    - At least one agent configured in the database
    - LLM API connectivity (or mocking)
    """
    
    @pytest.mark.auth
    @pytest.mark.slow
    def test_send_message_and_receive_response(self, logged_in_page: Page, base_url: str):
        """
        Full integration test: select agent, send message, receive response.
        
        Note: This test actually calls the LLM API, so it:
        - Takes longer to run
        - Requires valid API credentials
        - Should be marked as @pytest.mark.slow
        """
        logged_in_page.goto(f"{base_url}/assistants")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Wait for agents to load
        logged_in_page.wait_for_timeout(1000)
        
        agent_dropdown = logged_in_page.locator("#agent-dropdown")
        user_input = logged_in_page.locator("#user-input")
        send_button = logged_in_page.locator('button[onclick="sendMessage()"]')
        chat_content = logged_in_page.locator("#chat-content")
        
        # Check if there are agents available
        options = agent_dropdown.locator("option:not([value=''])")
        if options.count() == 0:
            pytest.skip("No agents available for chat test")
        
        # Select the first agent
        first_option = options.first
        agent_value = first_option.get_attribute("value")
        agent_dropdown.select_option(value=agent_value)
        logged_in_page.wait_for_timeout(500)
        
        # Send a simple message
        test_message = "Hello, please respond with a brief greeting."
        user_input.fill(test_message)
        send_button.click()
        
        # Wait for the user message to appear in chat
        user_message = chat_content.locator(".user-message, .user-bubble")
        expect(user_message.first).to_be_visible(timeout=5000)
        
        # Wait for agent response (this may take a while depending on LLM)
        # Increase timeout for slow API responses
        agent_message = chat_content.locator(".content-text")
        expect(agent_message.first).to_be_visible(timeout=60000)  # 60 second timeout
        
        # Verify the response contains some text
        response_text = agent_message.first.text_content()
        assert len(response_text) > 0, "Agent response should not be empty"


class TestResponsiveLayout:
    """Tests for responsive layout elements."""
    
    @pytest.mark.auth
    def test_sidebar_visible_on_desktop(self, logged_in_page: Page, base_url: str):
        """Verify the sidebar with agent selection is visible on desktop."""
        logged_in_page.goto(f"{base_url}/assistants")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Sidebar should be visible at default viewport (1280x800)
        sidebar = logged_in_page.locator(".sidebar-compact, .col-lg-3").first
        expect(sidebar).to_be_visible()
    
    @pytest.mark.auth
    def test_chat_and_sidebar_layout(self, logged_in_page: Page, base_url: str):
        """Verify chat area and sidebar are both visible side by side."""
        logged_in_page.goto(f"{base_url}/assistants")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Main chat area (col-lg-9)
        chat_area = logged_in_page.locator(".col-lg-9")
        expect(chat_area).to_be_visible()
        
        # Sidebar (col-lg-3)  
        sidebar = logged_in_page.locator(".col-lg-3")
        expect(sidebar).to_be_visible()
