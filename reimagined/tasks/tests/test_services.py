from unittest.mock import patch, Mock
from django.test import TestCase
from django.conf import settings
from django.db import IntegrityError
from tasks.models import TaskList, Task
from tasks.services import ClaudeTaskGroomer


class TestTaskGroomer(TestCase):
    def setUp(self):
        # Clear any existing tasks to ensure clean test state
        Task.objects.all().delete()
        TaskList.objects.all().delete()
        
        self.sample_todo = """
        Do laundry - wash and dry clothes
        Buy groceries for the week
        Clean the kitchen after cooking
        Call mom to check in
        """

    def test_task_groomer_initialization(self):
        groomer = ClaudeTaskGroomer()
        self.assertIsNotNone(groomer.api_key)

    @patch('tasks.services.requests.post')
    def test_groom_tasks_returns_structured_data(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": [{
                "text": '{"analysis": "Test analysis", "tasks": [{"task": "Do laundry", "task_id": "1234", "time_estimate": "02:00", "priority": "high", "dependencies": []}]}'
            }]
        }
        mock_post.return_value = mock_response
        
        groomer = ClaudeTaskGroomer()
        result = groomer.groom_tasks(self.sample_todo)
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["tasks"]), 1)
        self.assertEqual(result["tasks"][0]["task"], "Do laundry")
        self.assertEqual(result["tasks"][0]["task_id"], "1234")

    @patch('tasks.services.requests.post')
    def test_groom_tasks_handles_api_error(self, mock_post):
        mock_post.side_effect = Exception("API Error")
        
        groomer = ClaudeTaskGroomer()
        result = groomer.groom_tasks(self.sample_todo)
        
        self.assertFalse(result["success"])
        self.assertIn("error", result)

    @patch('tasks.services.requests.post')
    def test_groom_tasks_handles_invalid_json(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": [{"text": "Invalid JSON response"}]
        }
        mock_post.return_value = mock_response
        
        groomer = ClaudeTaskGroomer()
        result = groomer.groom_tasks(self.sample_todo)
        
        self.assertFalse(result["success"])
        self.assertIn("error", result)

    def test_create_task_list_from_groomed_tasks(self):
        groomed_result = {
            "success": True,
            "analysis": "Test analysis",
            "tasks": [
                {
                    "task": "Do laundry",
                    "task_id": "1234",
                    "time_estimate": "02:00",
                    "priority": "high",
                    "dependencies": []
                },
                {
                    "task": "Buy groceries",
                    "task_id": "5678",
                    "time_estimate": "00:45",
                    "priority": "medium",
                    "dependencies": ["1234"]
                }
            ]
        }
        
        groomer = ClaudeTaskGroomer()
        task_list, analysis = groomer.create_task_list_from_groomed_tasks(
            "Weekly Tasks", 
            self.sample_todo,
            groomed_result
        )
        
        self.assertEqual(task_list.name, "Weekly Tasks")
        self.assertEqual(task_list.raw_input, self.sample_todo)
        self.assertEqual(task_list.tasks.count(), 2)
        
        laundry_task = task_list.tasks.get(title="Do laundry")
        grocery_task = task_list.tasks.get(title="Buy groceries")
        
        self.assertEqual(laundry_task.estimated_duration, 120)
        self.assertEqual(laundry_task.task_id, "1234")
        self.assertEqual(grocery_task.estimated_duration, 45)
        self.assertEqual(grocery_task.task_id, "5678")

    @patch('tasks.services.requests.post')
    def test_process_todo_full_workflow(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": [{
                "text": '{"analysis": "Kitchen task breakdown", "tasks": [{"task": "Clean kitchen", "task_id": "abcd", "time_estimate": "00:30", "priority": "medium", "dependencies": []}]}'
            }]
        }
        mock_post.return_value = mock_response
        
        groomer = ClaudeTaskGroomer()
        task_list, analysis = groomer.process_todo("Kitchen Tasks", self.sample_todo)
        
        self.assertIsInstance(task_list, TaskList)
        self.assertEqual(task_list.name, "Kitchen Tasks")
        self.assertEqual(task_list.tasks.count(), 1)
        
        task = task_list.tasks.first()
        self.assertEqual(task.title, "Clean kitchen")
        self.assertEqual(task.estimated_duration, 30)

    def test_duplicate_task_id_causes_integrity_error(self):
        """Test that demonstrates the bug - duplicate task_ids cause IntegrityError"""  
        # First create a task with task_id "1234"
        Task.objects.create(
            title="Existing task",
            description="An existing task", 
            task_id="1234",
            estimated_duration=30,
            priority="medium"
        )
        
        # Now try to create another task with the same task_id directly
        with self.assertRaises(IntegrityError):
            Task.objects.create(
                title="Duplicate task",
                description="This should fail",
                task_id="1234",  # Same ID - should cause IntegrityError
                estimated_duration=45,
                priority="high"
            )

    def test_service_level_duplicate_task_id_bug(self):
        """Test that reproduces the real-world service bug with duplicate task_ids"""
        groomed_result = {
            "success": True,
            "analysis": "Test analysis",
            "tasks": [
                {
                    "task": "First task",
                    "task_id": "abcd",
                    "time_estimate": "00:30",
                    "priority": "high",
                    "dependencies": []
                },
                {
                    "task": "Second task with same ID", 
                    "task_id": "abcd",  # Same ID - this reproduces the bug
                    "time_estimate": "00:45",
                    "priority": "medium",
                    "dependencies": []
                }
            ]
        }
        
        groomer = ClaudeTaskGroomer()
        
        # This currently raises IntegrityError, proving the bug exists
        with self.assertRaises(IntegrityError):
            groomer.create_task_list_from_groomed_tasks(
                "Test List",
                "test input",
                groomed_result
            )

    def test_task_creation_should_generate_unique_ids(self):
        """Test that task creation should generate unique IDs when duplicates are provided"""
        groomed_result = {
            "success": True,
            "analysis": "Test analysis", 
            "tasks": [
                {
                    "task": "First task",
                    "task_id": "abcd",
                    "time_estimate": "00:30",
                    "priority": "high",
                    "dependencies": []
                },
                {
                    "task": "Second task",
                    "task_id": "efgh",
                    "time_estimate": "00:45",
                    "priority": "medium", 
                    "dependencies": []
                },
                {
                    "task": "Third task",
                    "task_id": "ijkl",
                    "time_estimate": "01:00",
                    "priority": "low",
                    "dependencies": []
                }
            ]
        }
        
        groomer = ClaudeTaskGroomer()
        task_list, _ = groomer.create_task_list_from_groomed_tasks(
            "Test List",
            "test input",
            groomed_result
        )
        
        # All tasks should be created successfully
        self.assertEqual(task_list.tasks.count(), 3)
        
        # All task_ids should be unique
        task_ids = list(task_list.tasks.values_list('task_id', flat=True))
        self.assertEqual(len(task_ids), len(set(task_ids)))  # No duplicates
        
        # Verify specific task_ids are preserved
        self.assertIn('abcd', task_ids)
        self.assertIn('efgh', task_ids) 
        self.assertIn('ijkl', task_ids)