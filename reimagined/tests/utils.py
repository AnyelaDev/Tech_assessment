"""
Test utilities and helper functions
"""
import os
from django.test import TestCase
from django.conf import settings
from tasks.models import TaskList, Task
from tasks.services import ClaudeTaskGroomer


class BaseClaudeTestCase(TestCase):
    """Base test case with common Claude testing setup"""
    
    def setUp(self):
        """Common setup for Claude tests"""
        self.groomer = ClaudeTaskGroomer()
        
    def create_test_task_list(self, name="Test List", raw_input="Test todo"):
        """Create a test TaskList for testing"""
        return TaskList.objects.create(name=name, raw_input=raw_input)
    
    def create_test_task(self, task_list=None, **kwargs):
        """Create a test Task with default values"""
        if task_list is None:
            task_list = self.create_test_task_list()
            
        defaults = {
            'title': 'Test Task',
            'description': 'Test Description',
            'task_id': 'test123',
            'priority': 'medium',
            'estimated_duration': 30,
            'task_list': task_list
        }
        defaults.update(kwargs)
        
        return Task.objects.create(**defaults)
    
    def assert_task_structure(self, task_data):
        """Assert that a task data dict has the required structure"""
        required_fields = ['task', 'task_id', 'time_estimate', 'priority']
        for field in required_fields:
            self.assertIn(field, task_data, f"Missing required field: {field}")
        
        # Validate priority
        self.assertIn(task_data['priority'], ['low', 'medium', 'high'])
        
        # Validate task_id format (should be hex-like)
        self.assertRegex(task_data['task_id'], r'^[a-f0-9]+$', 
                        "task_id should be hexadecimal")
        
        # Validate time_estimate format (should be hh:mm)
        self.assertRegex(task_data['time_estimate'], r'^\d{1,2}:\d{2}$',
                        "time_estimate should be in hh:mm format")
    
    def assert_claude_response_structure(self, response):
        """Assert that a Claude API response has the expected structure"""
        self.assertIn('success', response)
        
        if response['success']:
            self.assertIn('analysis', response)
            self.assertIn('tasks', response)
            self.assertIsInstance(response['tasks'], list)
            
            for task in response['tasks']:
                self.assert_task_structure(task)
        else:
            self.assertIn('error', response)
    
    def count_tasks_by_priority(self, tasks):
        """Count tasks by priority level"""
        counts = {'high': 0, 'medium': 0, 'low': 0}
        for task in tasks:
            priority = task.get('priority', 'medium')
            if priority in counts:
                counts[priority] += 1
        return counts


class ClaudeTestSkipMixin:
    """Mixin to skip tests when Claude API key is not available"""
    
    def skip_if_no_claude_key(self):
        """Skip test if Claude API key is not configured"""
        if not hasattr(settings, 'CLAUDE_API_KEY') or not settings.CLAUDE_API_KEY:
            self.skipTest("CLAUDE_API_KEY not configured - skipping integration test")
    
    def skip_if_claude_key_invalid(self):
        """Skip test if Claude API key appears to be placeholder"""
        if (not hasattr(settings, 'CLAUDE_API_KEY') or 
            not settings.CLAUDE_API_KEY or
            'your_claude_api_key_here' in settings.CLAUDE_API_KEY.lower()):
            self.skipTest("Valid CLAUDE_API_KEY required for integration test")


def assert_time_parsing_valid(test_case, time_str, expected_minutes):
    """Helper to test time parsing"""
    groomer = ClaudeTaskGroomer()
    result = groomer.parse_time_estimate(time_str)
    test_case.assertEqual(result, expected_minutes,
                         f"Time parsing '{time_str}' expected {expected_minutes}, got {result}")


def assert_database_has_tasks(test_case, task_list, expected_count=None):
    """Assert that tasks were properly saved to database"""
    tasks = task_list.tasks.all()
    
    if expected_count:
        test_case.assertEqual(tasks.count(), expected_count)
    
    for task in tasks:
        # Verify required fields are set
        test_case.assertTrue(task.title)
        test_case.assertTrue(task.task_id)
        test_case.assertIn(task.priority, ['low', 'medium', 'high'])
        test_case.assertGreater(task.estimated_duration, 0)
        
        # Verify task_id is not default
        test_case.assertNotEqual(task.task_id, "00000000")


def clean_test_data():
    """Clean up test data - useful for integration tests"""
    # Delete any TaskLists created during testing
    TaskList.objects.filter(name__icontains='test').delete()
    TaskList.objects.filter(name__icontains='Test').delete()


# Decorator for integration tests
def requires_claude_api(test_func):
    """Decorator to skip test if Claude API is not available"""
    def wrapper(self, *args, **kwargs):
        if (not hasattr(settings, 'CLAUDE_API_KEY') or 
            not settings.CLAUDE_API_KEY or
            'your_claude_api_key_here' in settings.CLAUDE_API_KEY.lower()):
            self.skipTest("Valid CLAUDE_API_KEY required")
        return test_func(self, *args, **kwargs)
    return wrapper