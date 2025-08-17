"""
Django Unit Tests for Claude Integration
"""
import json
from unittest.mock import patch, Mock
from django.test import TestCase
from django.conf import settings
from tasks.services import ClaudeTaskGroomer
from tasks.models import TaskList, Task


class TestClaudeTaskGroomer(TestCase):
    """Test suite for ClaudeTaskGroomer service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.groomer = ClaudeTaskGroomer()
        self.mock_claude_response = {
            "analysis": "Test analysis of the todo breakdown",
            "tasks": [
                {
                    "task": "Complete first task",
                    "task_id": "a101",
                    "time_estimate": "01:30",
                    "dependencies": [],
                    "priority": "high"
                },
                {
                    "task": "Complete second task", 
                    "task_id": "a102",
                    "time_estimate": "00:45",
                    "dependencies": ["a101"],
                    "priority": "medium"
                }
            ]
        }
    
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
                result = self.groomer.parse_time_estimate(time_str)
                self.assertEqual(result, expected)
    
    def test_time_parsing_invalid_formats(self):
        """Test time estimate parsing with invalid formats defaults to 30"""
        invalid_formats = ["invalid", "", "1:2:3", "abc:def", "60", None]
        
        for invalid_format in invalid_formats:
            with self.subTest(format=invalid_format):
                result = self.groomer.parse_time_estimate(str(invalid_format) if invalid_format else "")
                self.assertEqual(result, 30)
    
    @patch('tasks.services.requests.post')
    def test_groom_tasks_success(self, mock_post):
        """Test successful Claude API call and response parsing"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'content': [{'text': json.dumps(self.mock_claude_response)}]
        }
        mock_post.return_value = mock_response
        
        result = self.groomer.groom_tasks("Test todo text")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['analysis'], "Test analysis of the todo breakdown")
        self.assertEqual(len(result['tasks']), 2)
        self.assertEqual(result['tasks'][0]['task'], "Complete first task")
        
        # Verify API call was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], 'https://api.anthropic.com/v1/messages')
    
    @patch('tasks.services.requests.post')
    def test_groom_tasks_api_error(self, mock_post):
        """Test handling of API errors"""
        # Mock API error
        mock_post.side_effect = Exception("API connection failed")
        
        result = self.groomer.groom_tasks("Test todo text")
        
        self.assertFalse(result['success'])
        self.assertIn('API connection failed', result['error'])
        self.assertEqual(result['analysis'], "")
        self.assertEqual(result['tasks'], [])
    
    @patch('tasks.services.requests.post')
    def test_groom_tasks_invalid_json(self, mock_post):
        """Test handling of invalid JSON response"""
        # Mock response with invalid JSON
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'content': [{'text': 'Invalid JSON response'}]
        }
        mock_post.return_value = mock_response
        
        result = self.groomer.groom_tasks("Test todo text")
        
        self.assertFalse(result['success'])
        self.assertIn('JSON', result['error'])
    
    def test_create_task_list_success(self):
        """Test successful TaskList and Task creation"""
        mock_result = {
            'success': True,
            'analysis': 'Test analysis',
            'tasks': self.mock_claude_response['tasks']
        }
        
        task_list, analysis = self.groomer.create_task_list_from_groomed_tasks(
            "Test List", "Original todo text", mock_result
        )
        
        # Verify TaskList creation
        self.assertIsInstance(task_list, TaskList)
        self.assertEqual(task_list.name, "Test List")
        self.assertEqual(task_list.raw_input, "Original todo text")
        self.assertEqual(analysis, "Test analysis")
        
        # Verify Tasks creation
        tasks = task_list.tasks.all()
        self.assertEqual(tasks.count(), 2)
        
        first_task = tasks.get(task_id="a101")
        self.assertEqual(first_task.title, "Complete first task")
        self.assertEqual(first_task.priority, "high")
        self.assertEqual(first_task.estimated_duration, 90)  # 01:30 = 90 minutes
        
        second_task = tasks.get(task_id="a102")
        self.assertEqual(second_task.title, "Complete second task")
        self.assertEqual(second_task.priority, "medium")
        self.assertEqual(second_task.estimated_duration, 45)  # 00:45 = 45 minutes
        
        # Verify dependency relationship
        self.assertEqual(second_task.dependencies.count(), 1)
        self.assertEqual(second_task.dependencies.first(), first_task)
    
    def test_create_task_list_failure(self):
        """Test handling of failed Claude result"""
        mock_result = {
            'success': False,
            'error': 'Claude API failed',
            'analysis': '',
            'tasks': []
        }
        
        with self.assertRaises(ValueError) as context:
            self.groomer.create_task_list_from_groomed_tasks(
                "Test List", "Original todo text", mock_result
            )
        
        self.assertIn('Claude API failed', str(context.exception))
    
    @patch.object(ClaudeTaskGroomer, 'groom_tasks')
    @patch.object(ClaudeTaskGroomer, 'create_task_list_from_groomed_tasks')
    def test_process_todo_integration(self, mock_create, mock_groom):
        """Test full process_todo workflow"""
        # Mock the groom_tasks response
        mock_groom.return_value = {
            'success': True,
            'analysis': 'Test analysis',
            'tasks': []
        }
        
        # Mock the create_task_list response
        mock_task_list = Mock()
        mock_create.return_value = (mock_task_list, 'Test analysis')
        
        task_list, analysis = self.groomer.process_todo("Test Name", "Test todo", "Test context")
        
        # Verify method calls
        mock_groom.assert_called_once_with("Test todo", "Test context")
        mock_create.assert_called_once()
        
        # Verify return values
        self.assertEqual(task_list, mock_task_list)
        self.assertEqual(analysis, 'Test analysis')
    
    def test_task_model_fields(self):
        """Test that Task model has all required new fields"""
        # Create a task to test field existence
        task_list = TaskList.objects.create(name="Test", raw_input="Test input")
        task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            task_id="test123",
            priority="high",
            estimated_duration=60,
            task_list=task_list
        )
        
        # Verify all fields exist and are set correctly
        self.assertEqual(task.task_id, "test123")
        self.assertEqual(task.priority, "high")
        self.assertEqual(task.estimated_duration, 60)
        self.assertIn(task.priority, ['low', 'medium', 'high'])
    
    def test_priority_choices(self):
        """Test that priority field accepts valid choices"""
        task_list = TaskList.objects.create(name="Test", raw_input="Test")
        
        valid_priorities = ['low', 'medium', 'high']
        for priority in valid_priorities:
            with self.subTest(priority=priority):
                task = Task.objects.create(
                    title=f"Task {priority}",
                    description="Test",
                    task_id=f"test_{priority}",
                    priority=priority,
                    estimated_duration=30,
                    task_list=task_list
                )
                self.assertEqual(task.priority, priority)


class TestClaudeTaskGroomerIntegration(TestCase):
    """Integration tests that require actual API calls"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        if not hasattr(settings, 'CLAUDE_API_KEY') or not settings.CLAUDE_API_KEY:
            self.skipTest("CLAUDE_API_KEY not configured")
        
        self.groomer = ClaudeTaskGroomer()
    
    def test_real_api_call(self):
        """Test with actual Claude API call (requires API key)"""
        simple_todo = "Buy milk and walk the dog"
        
        result = self.groomer.groom_tasks(simple_todo)
        
        # Should succeed with valid API key
        self.assertTrue(result.get('success'), f"API call failed: {result.get('error')}")
        self.assertIn('analysis', result)
        self.assertIn('tasks', result)
        self.assertIsInstance(result['tasks'], list)
        self.assertGreater(len(result['tasks']), 0)
        
        # Verify task structure
        for task in result['tasks']:
            self.assertIn('task', task)
            self.assertIn('task_id', task)
            self.assertIn('priority', task)
            self.assertIn('time_estimate', task)
    
    def test_full_workflow_with_real_api(self):
        """Test complete workflow from todo text to saved tasks"""
        test_todo = "Prepare presentation for Monday meeting"
        
        task_list, analysis = self.groomer.process_todo("Integration Test", test_todo)
        
        # Verify TaskList was created and saved
        self.assertIsInstance(task_list, TaskList)
        self.assertTrue(task_list.pk)  # Should have database ID
        self.assertEqual(task_list.name, "Integration Test")
        self.assertEqual(task_list.raw_input, test_todo)
        
        # Verify Tasks were created
        tasks = task_list.tasks.all()
        self.assertGreater(tasks.count(), 0)
        
        # Verify analysis was provided
        self.assertTrue(analysis)
        self.assertIsInstance(analysis, str)
        
        # Verify task data integrity
        for task in tasks:
            self.assertTrue(task.title)
            self.assertTrue(task.task_id)
            self.assertIn(task.priority, ['low', 'medium', 'high'])
            self.assertGreater(task.estimated_duration, 0)
        
        # Clean up
        task_list.delete()