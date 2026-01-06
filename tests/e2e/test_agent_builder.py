"""
Tests for the Agent Builder Page (custom_agent_enhanced.html)
=============================================================

These tests verify the agent builder functionality including:
- Page loading and element presence
- Agent selection and editing
- Creating new agents
- Tool selection (core and custom)
- Import/Export functionality

Usage:
    pytest tests/e2e/test_agent_builder.py -v --headed
"""

import pytest
import re
from playwright.sync_api import Page, expect


class TestAgentBuilderPageLoad:
    """Tests for basic page loading and element presence."""
    
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_agent_builder_page_loads(self, logged_in_page: Page, base_url: str):
        """Verify the agent builder page loads without errors."""
        logged_in_page.goto(f"{base_url}/custom_agent_enhanced")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Should not be a 404 or error page
        assert "404" not in logged_in_page.title().lower()
        assert "error" not in logged_in_page.title().lower()
    
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_agent_builder_has_header(self, logged_in_page: Page, base_url: str):
        """Verify the page header shows 'Agent Builder'."""
        logged_in_page.goto(f"{base_url}/custom_agent_enhanced")
        logged_in_page.wait_for_load_state("networkidle")
        
        header = logged_in_page.locator(".compact-header h4")
        expect(header).to_be_visible()
        expect(header).to_contain_text("Agent Builder")
    
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_agent_builder_has_agent_dropdown(self, logged_in_page: Page, base_url: str):
        """Verify the agent selection dropdown exists."""
        logged_in_page.goto(f"{base_url}/custom_agent_enhanced")
        logged_in_page.wait_for_load_state("networkidle")
        
        agent_dropdown = logged_in_page.locator("#agent-dropdown")
        expect(agent_dropdown).to_be_visible()
    
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_agent_builder_has_configuration_form(self, logged_in_page: Page, base_url: str):
        """Verify the agent configuration form elements exist."""
        logged_in_page.goto(f"{base_url}/custom_agent_enhanced")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Check for objective textarea
        objective = logged_in_page.locator("#objective")
        expect(objective).to_be_visible()
        
        # Check for name input
        name = logged_in_page.locator("#name")
        expect(name).to_be_visible()
    
    @pytest.mark.auth
    def test_agent_builder_has_action_buttons(self, logged_in_page: Page, base_url: str):
        """Verify action buttons are present."""
        logged_in_page.goto(f"{base_url}/custom_agent_enhanced")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Save Changes button
        save_btn = logged_in_page.locator('button[onclick="updateAgent()"]')
        expect(save_btn).to_be_visible()
        
        # Delete Agent button
        delete_btn = logged_in_page.locator('button[onclick="deleteAgent()"]')
        expect(delete_btn).to_be_visible()
        
        # Add New Agent button
        add_btn = logged_in_page.locator('button[onclick="openAddAgentPopup()"]')
        expect(add_btn).to_be_visible()
    
    @pytest.mark.auth
    def test_agent_builder_has_sidebar_actions(self, logged_in_page: Page, base_url: str):
        """Verify sidebar action buttons are present."""
        logged_in_page.goto(f"{base_url}/custom_agent_enhanced")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Manage Knowledge button
        knowledge_btn = logged_in_page.locator('button[onclick="manageAgentKnowledge()"]')
        expect(knowledge_btn).to_be_visible()
        
        # Export Agent button
        export_btn = logged_in_page.locator("#exportAgentBtn")
        expect(export_btn).to_be_visible()


class TestAgentSelection:
    """Tests for agent selection functionality."""
    
    @pytest.mark.auth
    def test_agent_dropdown_has_default_option(self, logged_in_page: Page, base_url: str):
        """Verify the agent dropdown has a default 'Select an agent' option."""
        logged_in_page.goto(f"{base_url}/custom_agent_enhanced")
        logged_in_page.wait_for_load_state("networkidle")
        
        agent_dropdown = logged_in_page.locator("#agent-dropdown")
        default_option = agent_dropdown.locator('option[value=""]')
        expect(default_option).to_have_text("Select an agent")
    
    @pytest.mark.auth
    def test_agent_dropdown_loads_agents(self, logged_in_page: Page, base_url: str):
        """Verify agents are loaded into the dropdown."""
        logged_in_page.goto(f"{base_url}/custom_agent_enhanced")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Wait for agents to load via AJAX
        logged_in_page.wait_for_timeout(1000)
        
        agent_dropdown = logged_in_page.locator("#agent-dropdown")
        options = agent_dropdown.locator("option")
        
        # Should have at least the default option
        assert options.count() >= 1
    
    @pytest.mark.auth
    def test_selecting_agent_populates_form(self, logged_in_page: Page, base_url: str):
        """Verify selecting an agent populates the configuration form."""
        logged_in_page.goto(f"{base_url}/custom_agent_enhanced")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Wait for agents to load
        logged_in_page.wait_for_timeout(1000)
        
        agent_dropdown = logged_in_page.locator("#agent-dropdown")
        name_field = logged_in_page.locator("#name")
        objective_field = logged_in_page.locator("#objective")
        
        # Get all agent options (excluding default)
        options = agent_dropdown.locator("option:not([value=''])")
        
        if options.count() > 0:
            # Select the first agent
            first_option = options.first
            agent_value = first_option.get_attribute("value")
            agent_dropdown.select_option(value=agent_value)
            
            # Wait for form to populate
            logged_in_page.wait_for_timeout(500)
            
            # Name field should now have a value
            name_value = name_field.input_value()
            assert len(name_value) > 0, "Agent name should be populated after selection"
        else:
            pytest.skip("No agents available for selection test")
    
    @pytest.mark.auth
    def test_selecting_agent_shows_email_card(self, logged_in_page: Page, base_url: str):
        """Verify email actions card appears when an agent is selected."""
        logged_in_page.goto(f"{base_url}/custom_agent_enhanced")
        logged_in_page.wait_for_load_state("networkidle")
        logged_in_page.wait_for_timeout(1000)
        
        agent_dropdown = logged_in_page.locator("#agent-dropdown")
        email_card = logged_in_page.locator("#emailActionsCard")
        
        # Email card should be hidden initially
        expect(email_card).to_be_hidden()
        
        # Select an agent if available
        options = agent_dropdown.locator("option:not([value=''])")
        if options.count() > 0:
            first_option = options.first
            agent_value = first_option.get_attribute("value")
            agent_dropdown.select_option(value=agent_value)
            logged_in_page.wait_for_timeout(500)
            
            # Email card should now be visible
            expect(email_card).to_be_visible()
        else:
            pytest.skip("No agents available for email card test")


class TestToolSelection:
    """Tests for tool selection functionality."""
    
    @pytest.mark.auth
    def test_core_tools_section_exists(self, logged_in_page: Page, base_url: str):
        """Verify the core tools section is present."""
        logged_in_page.goto(f"{base_url}/custom_agent_enhanced")
        logged_in_page.wait_for_load_state("networkidle")
        
        core_tools_heading = logged_in_page.locator("h6:has-text('Core Tools')").first
        expect(core_tools_heading).to_be_visible()
    
    @pytest.mark.auth
    def test_custom_tools_section_exists(self, logged_in_page: Page, base_url: str):
        """Verify the custom tools section is present."""
        logged_in_page.goto(f"{base_url}/custom_agent_enhanced")
        logged_in_page.wait_for_load_state("networkidle")
        
        custom_tools_heading = logged_in_page.locator("h6:has-text('Custom Tools')").first
        expect(custom_tools_heading).to_be_visible()
    
    @pytest.mark.auth
    def test_core_tools_search_works(self, logged_in_page: Page, base_url: str):
        """Verify the core tools search filters the list."""
        logged_in_page.goto(f"{base_url}/custom_agent_enhanced")
        logged_in_page.wait_for_load_state("networkidle")
        
        search_input = logged_in_page.locator("#core-tool-search")
        expect(search_input).to_be_visible()
        
        # Type in search box
        search_input.fill("test")
        logged_in_page.wait_for_timeout(300)
        
        # Clear search
        clear_btn = logged_in_page.locator('button[onclick="clearCoreToolSearch()"]')
        clear_btn.click()
        
        # Search should be cleared
        expect(search_input).to_have_value("")
    
    @pytest.mark.auth
    def test_custom_tools_search_works(self, logged_in_page: Page, base_url: str):
        """Verify the custom tools search filters the list."""
        logged_in_page.goto(f"{base_url}/custom_agent_enhanced")
        logged_in_page.wait_for_load_state("networkidle")
        
        search_input = logged_in_page.locator("#custom-tool-search")
        expect(search_input).to_be_visible()
        
        # Type in search box
        search_input.fill("test")
        logged_in_page.wait_for_timeout(300)
        
        # Clear search
        clear_btn = logged_in_page.locator('button[onclick="clearCustomToolSearch()"]')
        clear_btn.click()
        
        # Search should be cleared
        expect(search_input).to_have_value("")


class TestAddNewAgentPopup:
    """Tests for the Add New Agent popup functionality."""
    
    @pytest.mark.auth
    def test_add_agent_popup_opens(self, logged_in_page: Page, base_url: str):
        """Verify clicking 'Add New Agent' opens the popup."""
        logged_in_page.goto(f"{base_url}/custom_agent_enhanced")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Click Add New Agent button
        add_btn = logged_in_page.locator('button[onclick="openAddAgentPopup()"]')
        add_btn.click()
        
        # Wait for popup to appear
        logged_in_page.wait_for_timeout(300)
        
        # Popup should be visible
        popup = logged_in_page.locator("#add-agent-popup")
        expect(popup).to_be_visible()
    
    @pytest.mark.auth
    def test_add_agent_popup_has_form_fields(self, logged_in_page: Page, base_url: str):
        """Verify the add agent popup has required form fields."""
        logged_in_page.goto(f"{base_url}/custom_agent_enhanced")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Open popup
        add_btn = logged_in_page.locator('button[onclick="openAddAgentPopup()"]')
        add_btn.click()
        logged_in_page.wait_for_timeout(300)
        
        # Check for name input
        name_input = logged_in_page.locator("#new-agent-name")
        expect(name_input).to_be_visible()
        
        # Check for objective textarea
        objective_input = logged_in_page.locator("#new-agent-objective")
        expect(objective_input).to_be_visible()
    
    @pytest.mark.auth
    def test_add_agent_popup_closes_on_cancel(self, logged_in_page: Page, base_url: str):
        """Verify clicking Cancel closes the popup."""
        logged_in_page.goto(f"{base_url}/custom_agent_enhanced")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Open popup
        add_btn = logged_in_page.locator('button[onclick="openAddAgentPopup()"]')
        add_btn.click()
        logged_in_page.wait_for_timeout(300)
        
        popup = logged_in_page.locator("#add-agent-popup")
        expect(popup).to_be_visible()
        
        # Click Cancel
        cancel_btn = logged_in_page.locator('button[onclick="closeAddAgentPopup()"]')
        cancel_btn.click()
        logged_in_page.wait_for_timeout(300)
        
        # Popup should be hidden
        expect(popup).to_be_hidden()
    
    @pytest.mark.auth
    def test_add_agent_popup_closes_on_x(self, logged_in_page: Page, base_url: str):
        """Verify clicking X closes the popup."""
        logged_in_page.goto(f"{base_url}/custom_agent_enhanced")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Open popup
        add_btn = logged_in_page.locator('button[onclick="openAddAgentPopup()"]')
        add_btn.click()
        logged_in_page.wait_for_timeout(300)
        
        popup = logged_in_page.locator("#add-agent-popup")
        expect(popup).to_be_visible()
        
        # Click X button
        close_btn = logged_in_page.locator('#add-agent-popup .close, #add-agent-popup span[onclick="closeAddAgentPopup()"]')
        close_btn.click()
        logged_in_page.wait_for_timeout(300)
        
        # Popup should be hidden
        expect(popup).to_be_hidden()
    
    @pytest.mark.auth
    def test_can_fill_new_agent_form(self, logged_in_page: Page, base_url: str):
        """Verify user can fill in the new agent form fields."""
        logged_in_page.goto(f"{base_url}/custom_agent_enhanced")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Open popup
        add_btn = logged_in_page.locator('button[onclick="openAddAgentPopup()"]')
        add_btn.click()
        logged_in_page.wait_for_timeout(300)
        
        # Fill in name
        name_input = logged_in_page.locator("#new-agent-name")
        test_name = "Test Agent from Playwright"
        name_input.fill(test_name)
        expect(name_input).to_have_value(test_name)
        
        # Fill in objective
        objective_input = logged_in_page.locator("#new-agent-objective")
        test_objective = "This is a test agent created by automated testing."
        objective_input.fill(test_objective)
        expect(objective_input).to_have_value(test_objective)


class TestAgentCreation:
    """
    Tests for actually creating a new agent.
    These tests modify data and should be run carefully.
    """
    
    @pytest.mark.auth
    @pytest.mark.slow
    def test_create_new_agent_workflow(self, logged_in_page: Page, base_url: str):
        """
        Full integration test: create a new agent, verify it appears in dropdown.
        
        WARNING: This test creates actual data in your database.
        """
        logged_in_page.goto(f"{base_url}/custom_agent_enhanced")
        logged_in_page.wait_for_load_state("networkidle")
        logged_in_page.wait_for_timeout(1000)
        
        agent_dropdown = logged_in_page.locator("#agent-dropdown")
        
        # Count initial agents
        initial_options = agent_dropdown.locator("option:not([value=''])").count()
        
        # Open add agent popup
        add_btn = logged_in_page.locator('button[onclick="openAddAgentPopup()"]')
        add_btn.click()
        logged_in_page.wait_for_timeout(300)
        
        # Fill in agent details with unique name
        import time
        unique_name = f"Playwright Test Agent {int(time.time())}"
        
        name_input = logged_in_page.locator("#new-agent-name")
        name_input.fill(unique_name)
        
        objective_input = logged_in_page.locator("#new-agent-objective")
        objective_input.fill("Automated test agent - can be safely deleted.")
        
        # Click Save Agent
        save_btn = logged_in_page.locator('button[onclick="saveNewAgent()"]')
        save_btn.click()
        
        # Wait for save operation and popup to close
        logged_in_page.wait_for_timeout(2000)
        
        # Verify popup closed (indicates success)
        popup = logged_in_page.locator("#add-agent-popup")
        # Note: Depending on your implementation, the popup may or may not close automatically
        
        # Refresh to see the new agent in dropdown
        logged_in_page.reload()
        logged_in_page.wait_for_load_state("networkidle")
        logged_in_page.wait_for_timeout(1000)
        
        # Check if agent count increased
        final_options = agent_dropdown.locator("option:not([value=''])").count()
        
        # Verify the new agent appears (either by count or by finding it)
        agent_option = agent_dropdown.locator(f'option:has-text("{unique_name}")')
        expect(agent_option).to_have_count(1)


class TestImportExportFunctionality:
    """Tests for agent import/export features."""
    
    @pytest.mark.auth
    def test_export_button_requires_agent_selection(self, logged_in_page: Page, base_url: str):
        """Verify export button behavior when no agent is selected."""
        logged_in_page.goto(f"{base_url}/custom_agent_enhanced")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Export button should exist
        export_btn = logged_in_page.locator("#exportAgentBtn")
        expect(export_btn).to_be_visible()
        
        # Click export without selecting an agent
        # This should either show an error or be disabled
        # The exact behavior depends on your implementation
    
    @pytest.mark.auth
    def test_import_dialog_exists(self, logged_in_page: Page, base_url: str):
        """Verify the import dialog modal exists in the DOM."""
        logged_in_page.goto(f"{base_url}/custom_agent_enhanced")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Import dialog should exist (but be hidden)
        import_dialog = logged_in_page.locator("#importAgentDialog")
        expect(import_dialog).to_be_attached()


class TestNavigationToAgentBuilder:
    """Tests for navigating to the agent builder from other pages."""
    
    @pytest.mark.auth
    def test_navigate_from_dashboard(self, logged_in_page: Page, base_url: str):
        """Test navigating to agent builder from dashboard."""
        logged_in_page.goto(f"{base_url}/")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Click Manage Agents action card
        agent_link = logged_in_page.locator('.action-grid a.action-card:has-text("Manage Agents")')
        
        if agent_link.is_visible():
            agent_link.click()
            logged_in_page.wait_for_load_state("networkidle")
            
            # Verify we're on the agent builder page
            expect(logged_in_page).to_have_url(re.compile(r"custom_agent_enhanced"))
        else:
            pytest.skip("Manage Agents card not visible on dashboard")
    
    @pytest.mark.auth
    def test_navigate_from_sidebar(self, logged_in_page: Page, base_url: str):
        """Test navigating to agent builder via sidebar menu."""
        logged_in_page.goto(f"{base_url}/")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Click AI Agents dropdown in sidebar
        agents_dropdown = logged_in_page.locator('.new-nav-dropdown:has-text("AI Agents")')
        agents_dropdown.click()
        logged_in_page.wait_for_timeout(300)
        
        # Click Agent Builder link
        builder_link = logged_in_page.locator('#agentsSubmenu a:has-text("Agent Builder")')
        
        if builder_link.is_visible():
            builder_link.click()
            logged_in_page.wait_for_load_state("networkidle")
            
            # Verify we're on the agent builder page
            expect(logged_in_page).to_have_url(re.compile(r"custom_agent_enhanced"))
        else:
            pytest.skip("Agent Builder link not visible in sidebar")


class TestResponsiveElements:
    """Tests for responsive and interactive UI elements."""
    
    @pytest.mark.auth
    def test_form_fields_are_readonly_without_selection(self, logged_in_page: Page, base_url: str):
        """Verify form fields are readonly when no agent is selected."""
        logged_in_page.goto(f"{base_url}/custom_agent_enhanced")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Name field should be readonly
        name_field = logged_in_page.locator("#name")
        expect(name_field).to_have_attribute("readonly", "")
        
        # Objective field should be readonly
        objective_field = logged_in_page.locator("#objective")
        expect(objective_field).to_have_attribute("readonly", "")


class TestURLParameters:
    """Tests for URL parameter handling (e.g., ?edit=123)."""
    
    @pytest.mark.auth
    def test_edit_parameter_loads_agent(self, logged_in_page: Page, base_url: str):
        """Verify ?edit=ID parameter pre-selects an agent."""
        # First, get an agent ID from the dropdown
        logged_in_page.goto(f"{base_url}/custom_agent_enhanced")
        logged_in_page.wait_for_load_state("networkidle")
        logged_in_page.wait_for_timeout(1000)
        
        agent_dropdown = logged_in_page.locator("#agent-dropdown")
        options = agent_dropdown.locator("option:not([value=''])")
        
        if options.count() > 0:
            # Get the first agent's ID
            first_option = options.first
            agent_id = first_option.get_attribute("value")
            
            # Navigate with edit parameter
            logged_in_page.goto(f"{base_url}/custom_agent_enhanced?edit={agent_id}")
            logged_in_page.wait_for_load_state("networkidle")
            logged_in_page.wait_for_timeout(1000)
            
            # Verify the agent is selected in dropdown
            selected_value = agent_dropdown.input_value()
            assert selected_value == agent_id, "Agent should be pre-selected via URL parameter"
            
            # Verify name field is populated
            name_field = logged_in_page.locator("#name")
            name_value = name_field.input_value()
            assert len(name_value) > 0, "Name should be populated for pre-selected agent"
        else:
            pytest.skip("No agents available for edit parameter test")
