"""
Unit Tests for Claude Service - Fast tests with mocked API calls
"""
from unittest.mock import patch, Mock
from django.test import TestCase

from tasks.services import ClaudeTaskGroomer
from tasks.models import TaskList, Task
from tests.utils import BaseClaudeTestCase, assert_time_parsing_valid
from tests.fixtures.claude_responses import (
    SIMPLE_TODO_RESPONSE, COMPLEX_TODO_RESPONSE, GROCERY_TODO_RESPONSE,
    mock_claude_success_response, mock_claude_error_response, 
    mock_claude_invalid_json_response
)


class TestClaudeTaskGroomerUnit(BaseClaudeTestCase):
    """Unit tests for ClaudeTaskGroomer - all API calls are mocked"""
    
    def test_time_parsing_valid_formats(self):
        """Test time estimate parsing with valid formats"""
        test_cases = [
            ("01:30", 90),
            ("00:15", 15),
            ("02:00", 120),
            ("0:30", 30),
            ("10:45", 645)
        ]
        
        for time_str, expected in test_cases:
            with self.subTest(time_str=time_str):
                assert_time_parsing_valid(self, time_str, expected)
    
    def test_time_parsing_invalid_formats(self):
        """Test time estimate parsing with invalid formats defaults to 30"""
        invalid_formats = ["invalid", "", "1:2:3", "abc:def", "60", "1:60", "-1:30"]
        
        for invalid_format in invalid_formats:
            with self.subTest(format=invalid_format):
                result = self.groomer.parse_time_estimate(str(invalid_format) if invalid_format else "")
                self.assertEqual(result, 30)
    
    def test_time_parsing_edge_cases(self):
        """Test edge cases for time parsing"""
        edge_cases = [
            ("0:00", 0),      # Zero time
            ("0:01", 1),      # Minimum time
            ("23:59", 1439),  # Maximum reasonable time
        ]
        
        for time_str, expected in edge_cases:
            with self.subTest(time_str=time_str):
                assert_time_parsing_valid(self, time_str, expected)
    
    @patch('tasks.services.requests.post')
    def test_groom_tasks_simple_success(self, mock_post):
        """Test successful Claude API call with simple response"""
        mock_post.return_value = mock_claude_success_response(SIMPLE_TODO_RESPONSE)
        
        result = self.groomer.groom_tasks("Call dentist")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['analysis'], SIMPLE_TODO_RESPONSE['analysis'])
        self.assertEqual(len(result['tasks']), 1)
        self.assert_claude_response_structure(result)
        
        # Verify API was called correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], 'https://api.anthropic.com/v1/messages')
    
    @patch('tasks.services.requests.post')
    def test_groom_tasks_complex_success(self, mock_post):
        """Test successful Claude API call with complex response with dependencies"""
        mock_post.return_value = mock_claude_success_response(COMPLEX_TODO_RESPONSE)
        
        result = self.groomer.groom_tasks("Prepare for job interview")
        
        self.assertTrue(result['success'])
        self.assertEqual(len(result['tasks']), 5)
        self.assert_claude_response_structure(result)
        
        # Check dependencies exist
        tasks_with_deps = [t for t in result['tasks'] if t.get('dependencies')]
        self.assertGreater(len(tasks_with_deps), 0, "Should have tasks with dependencies")
        
        # Check priority distribution
        priority_counts = self.count_tasks_by_priority(result['tasks'])
        self.assertGreater(priority_counts['high'], 0, "Should have high priority tasks")
    
    @patch('tasks.services.requests.post')
    def test_groom_tasks_api_error(self, mock_post):
        """Test handling of API connection errors"""
        mock_post.side_effect = Exception("API connection failed")
        
        result = self.groomer.groom_tasks("Test todo")
        
        self.assertFalse(result['success'])
        self.assertIn('API connection failed', result['error'])
        self.assertEqual(result['analysis'], "")
        self.assertEqual(result['tasks'], [])
    
    @patch('tasks.services.requests.post')
    def test_groom_tasks_http_error(self, mock_post):
        """Test handling of HTTP errors"""
        mock_post.return_value = mock_claude_error_response(500, "Internal Server Error")
        
        result = self.groomer.groom_tasks("Test todo")
        
        self.assertFalse(result['success'])
        self.assertIn('HTTP 500', result['error'])
    
    @patch('tasks.services.requests.post')
    def test_groom_tasks_invalid_json(self, mock_post):
        """Test handling of invalid JSON response"""
        mock_post.return_value = mock_claude_invalid_json_response()
        
        result = self.groomer.groom_tasks("Test todo")
        
        self.assertFalse(result['success'])
        self.assertIn('JSON', result['error'])
    
    @patch('tasks.services.requests.post')
    def test_create_task_list_success(self, mock_post):
        """Test successful TaskList and Task creation from Claude response"""
        mock_post.return_value = mock_claude_success_response(GROCERY_TODO_RESPONSE)
        
        # Use the groomer's method that processes the Claude response
        mock_result = {
            'success': True,
            'analysis': GROCERY_TODO_RESPONSE['analysis'],
            'tasks': GROCERY_TODO_RESPONSE['tasks']
        }
        
        task_list, analysis = self.groomer.create_task_list_from_groomed_tasks(
            "Test Grocery List", "Buy groceries and cook dinner", mock_result
        )
        
        # Verify TaskList creation
        self.assertIsInstance(task_list, TaskList)
        self.assertEqual(task_list.name, "Test Grocery List")
        self.assertEqual(task_list.raw_input, "Buy groceries and cook dinner")
        self.assertEqual(analysis, GROCERY_TODO_RESPONSE['analysis'])
        
        # Verify Tasks creation
        tasks = task_list.tasks.all()
        self.assertEqual(tasks.count(), 3)
        
        # Verify specific task details using title-based lookups
        list_task = tasks.get(title="Create grocery shopping list")
        self.assertEqual(list_task.title, "Create grocery shopping list")
        self.assertEqual(list_task.priority, "medium")
        self.assertEqual(list_task.estimated_duration, 15)  # 00:15 = 15 minutes
        # Verify database task_id is 4-hex format, not AI reference ID
        self.assertRegex(list_task.task_id, r'^[0-9a-f]{4}$')
        self.assertNotEqual(list_task.task_id, "a101")  # Should not match AI reference ID
        
        cook_task = tasks.get(title="Prepare and cook dinner")
        self.assertEqual(cook_task.title, "Prepare and cook dinner")
        self.assertEqual(cook_task.priority, "high")
        self.assertEqual(cook_task.estimated_duration, 45)  # 00:45 = 45 minutes
        self.assertRegex(cook_task.task_id, r'^[0-9a-f]{4}$')
        
        # Verify dependency relationships (using title-based lookups)
        shop_task = tasks.get(title="Go to grocery store and shop")
        self.assertEqual(shop_task.dependencies.count(), 1)
        self.assertEqual(shop_task.dependencies.first(), list_task)
        
        cook_task = tasks.get(title="Prepare and cook dinner") 
        self.assertEqual(cook_task.dependencies.count(), 1)
        self.assertEqual(cook_task.dependencies.first(), shop_task)
        
        # Verify all database task_ids are unique 4-hex format
        task_ids = [task.task_id for task in tasks]
        self.assertEqual(len(task_ids), len(set(task_ids)))  # All unique
        for task_id in task_ids:
            self.assertRegex(task_id, r'^[0-9a-f]{4}$')  # 4-hex format
    
    def test_create_task_list_failure(self):
        """Test handling of failed Claude result"""
        mock_result = {
            'success': False,
            'error': 'Claude API timeout',
            'analysis': '',
            'tasks': []
        }
        
        with self.assertRaises(ValueError) as context:
            self.groomer.create_task_list_from_groomed_tasks(
                "Test List", "Test todo", mock_result
            )
        
        self.assertIn('Claude API timeout', str(context.exception))
    
    @patch.object(ClaudeTaskGroomer, 'groom_tasks')
    def test_process_todo_integration_mocked(self, mock_groom):
        """Test full process_todo workflow with mocked groom_tasks"""
        # Mock the groom_tasks response
        mock_groom.return_value = {
            'success': True,
            'analysis': 'Test analysis',
            'tasks': SIMPLE_TODO_RESPONSE['tasks']
        }
        
        task_list, analysis = self.groomer.process_todo("Test Process", "Test todo", "Test context")
        
        # Verify method was called correctly
        mock_groom.assert_called_once_with("Test todo", "Test context")
        
        # Verify return values
        self.assertIsInstance(task_list, TaskList)
        self.assertEqual(task_list.name, "Test Process")
        self.assertEqual(analysis, 'Test analysis')
        
        # Verify tasks were created
        self.assertEqual(task_list.tasks.count(), 1)
        task = task_list.tasks.first()
        self.assertEqual(task.title, "Call dentist to schedule appointment")
        self.assertEqual(task.priority, "medium")
        self.assertEqual(task.estimated_duration, 5)  # 00:05 = 5 minutes
        # Verify database task_id is 4-hex format, not AI reference ID
        self.assertRegex(task.task_id, r'^[0-9a-f]{4}$')
        self.assertNotEqual(task.task_id, "a101")  # Should not match AI reference ID
    
    def test_task_model_field_validation(self):
        """Test that Task model fields accept valid values"""
        task_list = self.create_test_task_list()
        
        # Test valid priority values
        valid_priorities = ['low', 'medium', 'high']
        for priority in valid_priorities:
            with self.subTest(priority=priority):
                task = self.create_test_task(
                    task_list=task_list,
                    task_id=f"test_{priority}",
                    priority=priority
                )
                self.assertEqual(task.priority, priority)
        
        # Test task_id field
        task = self.create_test_task(task_list=task_list, task_id="abc123")
        self.assertEqual(task.task_id, "abc123")
        
        # Test estimated_duration
        task = self.create_test_task(task_list=task_list, estimated_duration=90)
        self.assertEqual(task.estimated_duration, 90)