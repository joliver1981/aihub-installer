"""
Tests for the Jobs/Scheduler Page (jobs.html)
==============================================

These tests verify the job scheduler functionality including:
- Page loading and element presence
- Job selection and editing
- Creating new jobs
- Scheduling jobs
- Job history viewing
- Testing jobs

Usage:
    pytest tests/e2e/test_jobs.py -v --headed
"""

import pytest
import re
from playwright.sync_api import Page, expect


# ============================================================================
# Helper Functions
# ============================================================================

def select_first_job(page: Page) -> bool:
    """
    Helper to select the first available job in the dropdown.
    Returns True if a job was selected, False if no jobs available.
    """
    page.wait_for_timeout(1000)  # Wait for jobs to load via AJAX
    job_dropdown = page.locator("#job_name")
    options = job_dropdown.locator("option:not([disabled])")
    if options.count() > 0:
        first_option = options.first
        job_value = first_option.get_attribute("value")
        job_dropdown.select_option(value=job_value)
        page.wait_for_timeout(500)  # Wait for form to enable
        return True
    return False


# ============================================================================
# Test Classes
# ============================================================================

class TestJobsPageLoad:
    """Tests for basic page loading and element presence."""
    
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_jobs_page_loads(self, logged_in_page: Page, base_url: str):
        """Verify the jobs page loads without errors."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Should not be a 404 or error page
        assert "404" not in logged_in_page.title().lower()
        assert "error" not in logged_in_page.title().lower()
    
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_jobs_page_has_header(self, logged_in_page: Page, base_url: str):
        """Verify the page header shows 'Intelligent Jobs'."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        header = logged_in_page.locator(".compact-header h4")
        expect(header).to_be_visible()
        expect(header).to_contain_text("Intelligent Jobs")
    
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_jobs_page_has_job_dropdown(self, logged_in_page: Page, base_url: str):
        """Verify the job selection dropdown exists."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        job_dropdown = logged_in_page.locator("#job_name")
        expect(job_dropdown).to_be_visible()
    
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_jobs_page_has_agent_dropdown(self, logged_in_page: Page, base_url: str):
        """Verify the agent selection dropdown exists."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        agent_dropdown = logged_in_page.locator("#agent-dropdown")
        expect(agent_dropdown).to_be_visible()
    
    @pytest.mark.smoke
    @pytest.mark.auth
    def test_jobs_page_has_description_field(self, logged_in_page: Page, base_url: str):
        """Verify the description/instructions textarea exists."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        description = logged_in_page.locator("#description")
        expect(description).to_be_visible()
    
    @pytest.mark.auth
    def test_jobs_page_has_on_off_switch(self, logged_in_page: Page, base_url: str):
        """Verify the on/off toggle switch exists."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        on_off_switch = logged_in_page.locator("#is_on")
        expect(on_off_switch).to_be_attached()


class TestJobsHeaderButtons:
    """Tests for header action buttons."""
    
    @pytest.mark.auth
    def test_schedule_job_button_exists(self, logged_in_page: Page, base_url: str):
        """Verify the Schedule Job button exists in header."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        schedule_btn = logged_in_page.locator('button[data-target="#scheduleJobModal"]')
        expect(schedule_btn).to_be_visible()
        expect(schedule_btn).to_contain_text("Schedule Job")
    
    @pytest.mark.auth
    def test_view_history_button_exists(self, logged_in_page: Page, base_url: str):
        """Verify the View Job History button exists in header."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        history_btn = logged_in_page.locator('button[data-target="#jobHistoryModal"]')
        expect(history_btn).to_be_visible()
        expect(history_btn).to_contain_text("View Job History")


class TestJobsFormButtons:
    """Tests for form action buttons."""
    
    @pytest.mark.auth
    def test_save_button_exists(self, logged_in_page: Page, base_url: str):
        """Verify the Save button exists."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        save_btn = logged_in_page.locator('button[onclick="addJob()"]')
        expect(save_btn).to_be_visible()
    
    @pytest.mark.auth
    def test_new_job_button_exists(self, logged_in_page: Page, base_url: str):
        """Verify the New Job button exists."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        new_btn = logged_in_page.locator('button[data-target="#newJobModal"]')
        expect(new_btn).to_be_visible()
        expect(new_btn).to_contain_text("New Job")
    
    @pytest.mark.auth
    def test_delete_button_exists(self, logged_in_page: Page, base_url: str):
        """Verify the Delete button exists."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        delete_btn = logged_in_page.locator('button[onclick="deleteJob()"]')
        expect(delete_btn).to_be_visible()
    
    @pytest.mark.auth
    def test_test_run_button_exists(self, logged_in_page: Page, base_url: str):
        """Verify the Test/Run button exists."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        test_btn = logged_in_page.locator('button[onclick="testJob()"]')
        expect(test_btn).to_be_visible()
        expect(test_btn).to_contain_text("Run")


class TestJobSelection:
    """Tests for job selection functionality."""
    
    @pytest.mark.auth
    def test_job_dropdown_loads_jobs(self, logged_in_page: Page, base_url: str):
        """Verify jobs are loaded into the dropdown."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Wait for jobs to load via AJAX
        logged_in_page.wait_for_timeout(1000)
        
        job_dropdown = logged_in_page.locator("#job_name")
        options = job_dropdown.locator("option")
        
        # Should have at least the default option
        assert options.count() >= 1
    
    @pytest.mark.auth
    def test_form_controls_disabled_without_selection(self, logged_in_page: Page, base_url: str):
        """Verify form controls are disabled when no job is selected."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        logged_in_page.wait_for_timeout(500)
        
        # Agent dropdown should be disabled
        agent_dropdown = logged_in_page.locator("#agent-dropdown")
        expect(agent_dropdown).to_be_disabled()
        
        # Description should be disabled
        description = logged_in_page.locator("#description")
        expect(description).to_be_disabled()
    
    @pytest.mark.auth
    def test_selecting_job_enables_form(self, logged_in_page: Page, base_url: str):
        """Verify selecting a job enables the form controls."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        agent_dropdown = logged_in_page.locator("#agent-dropdown")
        description = logged_in_page.locator("#description")
        
        if select_first_job(logged_in_page):
            # Controls should now be enabled
            expect(agent_dropdown).to_be_enabled()
            expect(description).to_be_enabled()
        else:
            pytest.skip("No jobs available for selection test")
    
    @pytest.mark.auth
    def test_selecting_job_populates_form(self, logged_in_page: Page, base_url: str):
        """Verify selecting a job populates the form fields."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        if select_first_job(logged_in_page):
            # Hidden job_id should be set
            job_id_field = logged_in_page.locator("#job_id")
            job_id_value = job_id_field.input_value()
            assert len(job_id_value) > 0, "Job ID should be populated after selection"
        else:
            pytest.skip("No jobs available for form population test")


class TestNewJobModal:
    """Tests for the New Job modal functionality."""
    
    @pytest.mark.auth
    def test_new_job_modal_opens(self, logged_in_page: Page, base_url: str):
        """Verify clicking 'New Job' opens the modal."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Click New Job button (this one is always enabled)
        new_btn = logged_in_page.locator('button[data-target="#newJobModal"]')
        new_btn.click()
        
        # Wait for modal to appear
        logged_in_page.wait_for_timeout(300)
        
        # Modal should be visible
        modal = logged_in_page.locator("#newJobModal")
        expect(modal).to_be_visible()
    
    @pytest.mark.auth
    def test_new_job_modal_has_form_fields(self, logged_in_page: Page, base_url: str):
        """Verify the new job modal has required form fields."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Open modal
        new_btn = logged_in_page.locator('button[data-target="#newJobModal"]')
        new_btn.click()
        logged_in_page.wait_for_timeout(300)
        
        # Check for job name input
        job_name = logged_in_page.locator("#newJobName")
        expect(job_name).to_be_visible()
        
        # Check for agent dropdown
        agent_dropdown = logged_in_page.locator("#new-agent-dropdown")
        expect(agent_dropdown).to_be_visible()
        
        # Check for description textarea
        description = logged_in_page.locator("#newJobDescription")
        expect(description).to_be_visible()
        
        # Check for on/off switch
        on_off_switch = logged_in_page.locator("#newJobSwitch")
        expect(on_off_switch).to_be_attached()
    
    @pytest.mark.auth
    def test_new_job_modal_has_save_button(self, logged_in_page: Page, base_url: str):
        """Verify the new job modal has a save button."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Open modal
        new_btn = logged_in_page.locator('button[data-target="#newJobModal"]')
        new_btn.click()
        logged_in_page.wait_for_timeout(300)
        
        # Check for save button
        save_btn = logged_in_page.locator("#saveNewJobButton")
        expect(save_btn).to_be_visible()
    
    @pytest.mark.auth
    def test_new_job_modal_closes_on_cancel(self, logged_in_page: Page, base_url: str):
        """Verify clicking Cancel closes the modal."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Open modal
        new_btn = logged_in_page.locator('button[data-target="#newJobModal"]')
        new_btn.click()
        logged_in_page.wait_for_timeout(300)
        
        modal = logged_in_page.locator("#newJobModal")
        expect(modal).to_be_visible()
        
        # Click Cancel
        cancel_btn = logged_in_page.locator('#newJobModal button[data-dismiss="modal"]').first
        cancel_btn.click()
        logged_in_page.wait_for_timeout(300)
        
        # Modal should be hidden
        expect(modal).to_be_hidden()
    
    @pytest.mark.auth
    def test_can_fill_new_job_form(self, logged_in_page: Page, base_url: str):
        """Verify user can fill in the new job form fields."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Open modal
        new_btn = logged_in_page.locator('button[data-target="#newJobModal"]')
        new_btn.click()
        logged_in_page.wait_for_timeout(300)
        
        # Fill in job name
        job_name = logged_in_page.locator("#newJobName")
        test_name = "Test Job from Playwright"
        job_name.fill(test_name)
        expect(job_name).to_have_value(test_name)
        
        # Fill in description
        description = logged_in_page.locator("#newJobDescription")
        test_desc = "This is a test job created by automated testing."
        description.fill(test_desc)
        expect(description).to_have_value(test_desc)


class TestScheduleJobModal:
    """Tests for the Schedule Job modal functionality."""
    
    @pytest.mark.auth
    def test_schedule_button_disabled_without_job(self, logged_in_page: Page, base_url: str):
        """Verify Schedule Job button is disabled when no job is selected."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        logged_in_page.wait_for_timeout(500)
        
        schedule_btn = logged_in_page.locator('button[data-target="#scheduleJobModal"]')
        expect(schedule_btn).to_be_disabled()
    
    @pytest.mark.auth
    def test_schedule_modal_opens(self, logged_in_page: Page, base_url: str):
        """Verify clicking 'Schedule Job' opens the modal after selecting a job."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Must select a job first - button is disabled otherwise
        if not select_first_job(logged_in_page):
            pytest.skip("No jobs available to select")
        
        # Click Schedule Job button
        schedule_btn = logged_in_page.locator('button[data-target="#scheduleJobModal"]')
        expect(schedule_btn).to_be_enabled()
        schedule_btn.click()
        
        # Wait for modal to appear
        logged_in_page.wait_for_timeout(300)
        
        # Modal should be visible
        modal = logged_in_page.locator("#scheduleJobModal")
        expect(modal).to_be_visible()
    
    @pytest.mark.auth
    def test_schedule_modal_has_form_fields(self, logged_in_page: Page, base_url: str):
        """Verify the schedule modal has required form fields."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Must select a job first
        if not select_first_job(logged_in_page):
            pytest.skip("No jobs available to select")
        
        # Open modal
        schedule_btn = logged_in_page.locator('button[data-target="#scheduleJobModal"]')
        schedule_btn.click()
        logged_in_page.wait_for_timeout(300)
        
        # Check for schedule name input
        schedule_name = logged_in_page.locator("#schedule_name")
        expect(schedule_name).to_be_visible()
        
        # Check for datetime picker
        datetime_picker = logged_in_page.locator("#schedule_datetime")
        expect(datetime_picker).to_be_visible()
        
        # Check for frequency dropdown
        frequency = logged_in_page.locator("#schedule_frequency")
        expect(frequency).to_be_visible()
        
        # Check for enabled switch
        enabled_switch = logged_in_page.locator("#schedule_enabled")
        expect(enabled_switch).to_be_attached()
    
    @pytest.mark.auth
    def test_schedule_modal_frequency_options(self, logged_in_page: Page, base_url: str):
        """Verify the frequency dropdown has correct options."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Must select a job first
        if not select_first_job(logged_in_page):
            pytest.skip("No jobs available to select")
        
        # Open modal
        schedule_btn = logged_in_page.locator('button[data-target="#scheduleJobModal"]')
        schedule_btn.click()
        logged_in_page.wait_for_timeout(300)
        
        frequency = logged_in_page.locator("#schedule_frequency")
        
        # Check for expected options
        hourly_option = frequency.locator('option[value="Hourly"]')
        expect(hourly_option).to_be_attached()
        
        daily_option = frequency.locator('option[value="Daily"]')
        expect(daily_option).to_be_attached()
        
        weekly_option = frequency.locator('option[value="Weekly"]')
        expect(weekly_option).to_be_attached()
    
    @pytest.mark.auth
    def test_schedule_modal_closes_on_cancel(self, logged_in_page: Page, base_url: str):
        """Verify clicking Cancel closes the modal."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Must select a job first
        if not select_first_job(logged_in_page):
            pytest.skip("No jobs available to select")
        
        # Open modal
        schedule_btn = logged_in_page.locator('button[data-target="#scheduleJobModal"]')
        schedule_btn.click()
        logged_in_page.wait_for_timeout(300)
        
        modal = logged_in_page.locator("#scheduleJobModal")
        expect(modal).to_be_visible()
        
        # Click Cancel
        cancel_btn = logged_in_page.locator('#scheduleJobModal button[data-dismiss="modal"]').first
        cancel_btn.click()
        logged_in_page.wait_for_timeout(300)
        
        # Modal should be hidden
        expect(modal).to_be_hidden()


class TestJobHistoryModal:
    """Tests for the Job History modal functionality."""
    
    @pytest.mark.auth
    def test_history_button_disabled_without_job(self, logged_in_page: Page, base_url: str):
        """Verify View Job History button is disabled when no job is selected."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        logged_in_page.wait_for_timeout(500)
        
        history_btn = logged_in_page.locator('button[data-target="#jobHistoryModal"]')
        expect(history_btn).to_be_disabled()
    
    @pytest.mark.auth
    def test_history_modal_opens(self, logged_in_page: Page, base_url: str):
        """Verify clicking 'View Job History' opens the modal after selecting a job."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Must select a job first - button is disabled otherwise
        if not select_first_job(logged_in_page):
            pytest.skip("No jobs available to select")
        
        # Click View Job History button
        history_btn = logged_in_page.locator('button[data-target="#jobHistoryModal"]')
        expect(history_btn).to_be_enabled()
        history_btn.click()
        
        # Wait for modal to appear
        logged_in_page.wait_for_timeout(300)
        
        # Modal should be visible
        modal = logged_in_page.locator("#jobHistoryModal")
        expect(modal).to_be_visible()
    
    @pytest.mark.auth
    def test_history_modal_has_date_picker(self, logged_in_page: Page, base_url: str):
        """Verify the history modal has a date picker."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Must select a job first
        if not select_first_job(logged_in_page):
            pytest.skip("No jobs available to select")
        
        # Open modal
        history_btn = logged_in_page.locator('button[data-target="#jobHistoryModal"]')
        history_btn.click()
        logged_in_page.wait_for_timeout(300)
        
        # Check for date picker
        date_picker = logged_in_page.locator("#historyDate")
        expect(date_picker).to_be_visible()
    
    @pytest.mark.auth
    def test_history_modal_has_search_button(self, logged_in_page: Page, base_url: str):
        """Verify the history modal has a search button."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Must select a job first
        if not select_first_job(logged_in_page):
            pytest.skip("No jobs available to select")
        
        # Open modal
        history_btn = logged_in_page.locator('button[data-target="#jobHistoryModal"]')
        history_btn.click()
        logged_in_page.wait_for_timeout(300)
        
        # Check for search button
        search_btn = logged_in_page.locator("#searchJobHistoryButton")
        expect(search_btn).to_be_visible()
    
    @pytest.mark.auth
    def test_history_modal_has_results_container(self, logged_in_page: Page, base_url: str):
        """Verify the history modal has a results container."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Must select a job first
        if not select_first_job(logged_in_page):
            pytest.skip("No jobs available to select")
        
        # Open modal
        history_btn = logged_in_page.locator('button[data-target="#jobHistoryModal"]')
        history_btn.click()
        logged_in_page.wait_for_timeout(300)
        
        # Check for results container
        results = logged_in_page.locator("#jobHistoryResults")
        expect(results).to_be_visible()
    
    @pytest.mark.auth
    def test_history_modal_closes(self, logged_in_page: Page, base_url: str):
        """Verify the history modal can be closed."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Must select a job first
        if not select_first_job(logged_in_page):
            pytest.skip("No jobs available to select")
        
        # Open modal
        history_btn = logged_in_page.locator('button[data-target="#jobHistoryModal"]')
        history_btn.click()
        logged_in_page.wait_for_timeout(300)
        
        modal = logged_in_page.locator("#jobHistoryModal")
        expect(modal).to_be_visible()
        
        # Click Close
        close_btn = logged_in_page.locator('#jobHistoryModal button[data-dismiss="modal"]').first
        close_btn.click()
        logged_in_page.wait_for_timeout(300)
        
        # Modal should be hidden
        expect(modal).to_be_hidden()


class TestJobCreation:
    """
    Tests for actually creating a new job.
    These tests modify data and should be run carefully.
    """
    
    @pytest.mark.auth
    @pytest.mark.slow
    def test_create_new_job_workflow(self, logged_in_page: Page, base_url: str):
        """
        Full integration test: create a new job, verify it appears in dropdown.
        
        WARNING: This test creates actual data in your database.
        """
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        logged_in_page.wait_for_timeout(1000)
        
        job_dropdown = logged_in_page.locator("#job_name")
        
        # Count initial jobs
        initial_options = job_dropdown.locator("option:not([disabled])").count()
        
        # Open new job modal
        new_btn = logged_in_page.locator('button[data-target="#newJobModal"]')
        new_btn.click()
        logged_in_page.wait_for_timeout(300)
        
        # Fill in job details with unique name
        import time
        unique_name = f"Playwright Test Job {int(time.time())}"
        
        job_name = logged_in_page.locator("#newJobName")
        job_name.fill(unique_name)
        
        description = logged_in_page.locator("#newJobDescription")
        description.fill("Automated test job - can be safely deleted.")
        
        # Select an agent if available
        agent_dropdown = logged_in_page.locator("#new-agent-dropdown")
        agent_options = agent_dropdown.locator("option:not([value=''])")
        if agent_options.count() > 0:
            first_agent = agent_options.first.get_attribute("value")
            agent_dropdown.select_option(value=first_agent)
        
        # Click Save
        save_btn = logged_in_page.locator("#saveNewJobButton")
        save_btn.click()
        
        # Wait for save operation
        logged_in_page.wait_for_timeout(2000)
        
        # Refresh to see the new job in dropdown
        logged_in_page.reload()
        logged_in_page.wait_for_load_state("networkidle")
        logged_in_page.wait_for_timeout(1000)
        
        # Check if job appears in dropdown
        job_option = job_dropdown.locator(f'option:has-text("{unique_name}")')
        expect(job_option).to_have_count(1)


class TestNavigationToJobs:
    """Tests for navigating to the jobs page from other pages."""
    
    @pytest.mark.auth
    def test_navigate_from_sidebar(self, logged_in_page: Page, base_url: str):
        """Test navigating to jobs via sidebar menu."""
        logged_in_page.goto(f"{base_url}/")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Click Agent Jobs link in sidebar
        jobs_link = logged_in_page.locator('.new-nav-link:has-text("Agent Jobs")')
        
        if jobs_link.is_visible():
            jobs_link.click()
            logged_in_page.wait_for_load_state("networkidle")
            
            # Verify we're on the jobs page
            expect(logged_in_page).to_have_url(re.compile(r"jobs"))
        else:
            pytest.skip("Agent Jobs link not visible in sidebar")
    
    @pytest.mark.auth
    def test_navigate_from_dashboard(self, logged_in_page: Page, base_url: str):
        """Test navigating to jobs from dashboard scheduled jobs section."""
        logged_in_page.goto(f"{base_url}/")
        logged_in_page.wait_for_load_state("networkidle")
        
        # Look for "Manage" link in Scheduled Jobs section
        manage_link = logged_in_page.locator('.dashboard-section:has-text("Scheduled Jobs") a:has-text("Manage")')
        
        if manage_link.is_visible():
            manage_link.click()
            logged_in_page.wait_for_load_state("networkidle")
            
            # Verify we're on the jobs page
            expect(logged_in_page).to_have_url(re.compile(r"jobs"))
        else:
            pytest.skip("Scheduled Jobs manage link not visible on dashboard")


class TestJobTestRun:
    """Tests for job test/run functionality."""
    
    @pytest.mark.auth
    def test_test_button_disabled_without_job(self, logged_in_page: Page, base_url: str):
        """Verify test button is disabled when no job is selected."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        logged_in_page.wait_for_timeout(500)
        
        test_btn = logged_in_page.locator('button[onclick="testJob()"]')
        expect(test_btn).to_be_disabled()
    
    @pytest.mark.auth
    def test_test_button_enabled_with_job(self, logged_in_page: Page, base_url: str):
        """Verify test button is enabled when a job is selected."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        if select_first_job(logged_in_page):
            # Test button should now be enabled
            test_btn = logged_in_page.locator('button[onclick="testJob()"]')
            expect(test_btn).to_be_enabled()
        else:
            pytest.skip("No jobs available for test button test")
    
    @pytest.mark.auth
    def test_result_container_exists(self, logged_in_page: Page, base_url: str):
        """Verify the test result display container exists."""
        logged_in_page.goto(f"{base_url}/jobs")
        logged_in_page.wait_for_load_state("networkidle")
        
        result_container = logged_in_page.locator("#test_result")
        expect(result_container).to_be_attached()
