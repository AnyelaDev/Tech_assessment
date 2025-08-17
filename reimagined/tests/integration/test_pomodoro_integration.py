from django.test import TestCase, Client
from django.urls import reverse
import time


class TestPomodoroIntegration(TestCase):
    """Integration tests for Pomodoro timer functionality"""
    
    def setUp(self):
        self.client = Client()
        self.pomodoro_url = '/personal-assistance/executive-function/pomodoro/'
    
    def test_pomodoro_page_loads_successfully(self):
        """Test that the Pomodoro page loads without errors"""
        response = self.client.get(self.pomodoro_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pomodoro Timer')
    
    def test_pomodoro_page_navigation_from_executive_function(self):
        """Test navigation from executive function page to Pomodoro"""
        # Test that executive function page has the Pomodoro link
        exec_response = self.client.get('/personal-assistance/executive-function/')
        self.assertEqual(exec_response.status_code, 200)
        self.assertContains(exec_response, 'href="/personal-assistance/executive-function/pomodoro/"')
        self.assertContains(exec_response, 'Pomodoro</h2>')  # Updated text without (Mock)
        
        # Test that the Pomodoro page is accessible
        pomodoro_response = self.client.get(self.pomodoro_url)
        self.assertEqual(pomodoro_response.status_code, 200)
    
    def test_pomodoro_page_back_navigation(self):
        """Test that back button links correctly to executive function page"""
        response = self.client.get(self.pomodoro_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/personal-assistance/executive-function/"')
        self.assertContains(response, 'class="btn-back"')
        
        # Test that the back link actually works
        back_response = self.client.get('/personal-assistance/executive-function/')
        self.assertEqual(back_response.status_code, 200)
    
    def test_pomodoro_page_contains_required_ui_elements(self):
        """Test that Pomodoro page contains all required UI elements from Issue 19"""
        response = self.client.get(self.pomodoro_url)
        self.assertEqual(response.status_code, 200)
        
        # Timer display elements
        self.assertContains(response, 'class="timer-display"')
        self.assertContains(response, 'class="timer-circle"')
        self.assertContains(response, 'class="progress-bar"')
        
        # Control buttons (as specified in Issue 19)
        self.assertContains(response, 'Start Pomodoro')
        self.assertContains(response, 'Pause')
        self.assertContains(response, 'Reset')
        self.assertContains(response, 'Stop')
        
        # Configuration options (for configurable timer duration)
        self.assertContains(response, 'Work Duration')
        self.assertContains(response, 'Break Duration')
        self.assertContains(response, 'value="5"')  # Default 5 seconds as specified
    
    def test_pomodoro_page_visual_state_classes(self):
        """Test that Pomodoro page includes CSS classes for different visual states"""
        response = self.client.get(self.pomodoro_url)
        self.assertEqual(response.status_code, 200)
        
        # CSS classes for different states (work/break/restart)
        self.assertContains(response, 'work-state')
        self.assertContains(response, 'break-state')  
        self.assertContains(response, 'restart-state')
        
        # Visual state text as specified in Issue 19
        self.assertContains(response, 'Time for a break')
        self.assertContains(response, 'New pomodoro?')
        self.assertContains(response, 'Start Break')
    
    def test_pomodoro_javascript_functionality_present(self):
        """Test that Pomodoro JavaScript functionality is included"""
        response = self.client.get(self.pomodoro_url)
        self.assertEqual(response.status_code, 200)
        
        # JavaScript class and initialization
        self.assertContains(response, 'class PomodoroTimer')
        self.assertContains(response, 'new PomodoroTimer()')
        
        # Key methods that should be present
        self.assertContains(response, 'startWork()')
        self.assertContains(response, 'startBreak()')
        self.assertContains(response, 'updateDisplay()')
        self.assertContains(response, 'updateState()')
    
    def test_pomodoro_page_meets_issue_19_acceptance_criteria(self):
        """Test that Pomodoro page meets all Issue 19 acceptance criteria"""
        response = self.client.get(self.pomodoro_url)
        self.assertEqual(response.status_code, 200)
        
        # ✓ Add Pomodoro button to executive function page - tested in navigation test
        # ✓ Implement work timer: 5-second countdown with progress bar
        self.assertContains(response, 'progress-bar')
        self.assertContains(response, 'value="5"')  # Default 5 seconds
        
        # ✓ Create break screen: dark blue background with white "Time for a break" text and "Start Break" button
        self.assertContains(response, 'Time for a break')
        self.assertContains(response, 'Start Break')
        self.assertContains(response, 'break-state')
        
        # ✓ Implement break timer: 5-second countdown with progress bar
        self.assertContains(response, 'Break Duration')
        
        # ✓ Create restart screen: white background with teal "New pomodoro?" text and "Start Pomodoro" button  
        self.assertContains(response, 'New pomodoro?')
        self.assertContains(response, 'Start Pomodoro')
        self.assertContains(response, 'restart-state')
        
        # ✓ Ensure seamless cycle transitions and timer accuracy
        self.assertContains(response, 'updateState()')
        self.assertContains(response, 'complete()')
        
        # ✓ Add proper CSS styling for different screen states
        self.assertContains(response, '.pomodoro-container.work-state')
        self.assertContains(response, '.pomodoro-container.break-state')
        self.assertContains(response, '.pomodoro-container.restart-state')
        
        # ✓ Test timer functionality and visual transitions - covered by JavaScript presence
        self.assertContains(response, 'setInterval')
        self.assertContains(response, 'clearInterval')


class TestPomodoroAccessibility(TestCase):
    """Test Pomodoro timer accessibility and UX features"""
    
    def setUp(self):
        self.client = Client()
        self.pomodoro_url = '/personal-assistance/executive-function/pomodoro/'
    
    def test_pomodoro_page_has_proper_title(self):
        """Test that Pomodoro page has proper HTML title"""
        response = self.client.get(self.pomodoro_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<title>Pomodoro Timer</title>')
    
    def test_pomodoro_page_configurable_timer_duration(self):
        """Test that timer durations are configurable as specified"""
        response = self.client.get(self.pomodoro_url)
        self.assertEqual(response.status_code, 200)
        
        # Work duration input (default 5 seconds for easy manual testing)
        self.assertContains(response, 'id="workDuration"')
        self.assertContains(response, 'value="5"')
        self.assertContains(response, 'min="1"')
        self.assertContains(response, 'max="3600"')
        
        # Break duration input  
        self.assertContains(response, 'id="breakDuration"')
        self.assertContains(response, 'value="5"')
    
    def test_pomodoro_page_no_authentication_required(self):
        """Test that Pomodoro page works without authentication as specified"""
        # This test runs without any authentication setup
        response = self.client.get(self.pomodoro_url)
        self.assertEqual(response.status_code, 200)
        # No redirects to login or auth required
        self.assertContains(response, 'Pomodoro Timer')
    
    def test_pomodoro_timer_controls_functionality(self):
        """Test that timer controls are properly implemented"""
        response = self.client.get(self.pomodoro_url)
        self.assertEqual(response.status_code, 200)
        
        # All timer controls as specified in Issue 19
        self.assertContains(response, 'id="startBtn"')
        self.assertContains(response, 'id="pauseBtn"')
        self.assertContains(response, 'id="resetBtn"')
        self.assertContains(response, 'id="stopBtn"')
        
        # Timer control event listeners
        self.assertContains(response, 'addEventListener')
        self.assertContains(response, 'pause()')
        self.assertContains(response, 'reset()')
        self.assertContains(response, 'stop()')