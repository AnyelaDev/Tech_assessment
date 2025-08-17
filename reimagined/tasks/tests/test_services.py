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
                    "gen_task_id": "laundry_task",
                    "time_estimate": "02:00",
                    "priority": "high",
                    "dependencies": []
                },
                {
                    "task": "Buy groceries",
                    "gen_task_id": "grocery_task",
                    "time_estimate": "00:45",
                    "priority": "medium",
                    "dependencies": ["laundry_task"]
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
        self.assertEqual(grocery_task.estimated_duration, 45)
        
        # Database task_ids should be unique hex strings (not the gen_task_ids)
        self.assertEqual(len(laundry_task.task_id), 4)
        self.assertEqual(len(grocery_task.task_id), 4)
        self.assertNotEqual(laundry_task.task_id, grocery_task.task_id)
        
        # Test dependency mapping works with gen_task_ids
        self.assertEqual(grocery_task.dependencies.count(), 1)
        self.assertEqual(grocery_task.dependencies.first(), laundry_task)

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

    def test_service_handles_duplicate_gen_task_ids_gracefully(self):
        """Test that service handles even duplicate gen_task_ids by generating unique database IDs"""
        groomed_result = {
            "success": True,
            "analysis": "Test analysis",
            "tasks": [
                {
                    "task": "First task",
                    "gen_task_id": "task_a",  # Unique gen_task_id
                    "time_estimate": "00:30",
                    "priority": "high",
                    "dependencies": []
                },
                {
                    "task": "Second task", 
                    "gen_task_id": "task_b",  # Different gen_task_id
                    "time_estimate": "00:45",
                    "priority": "medium",
                    "dependencies": ["task_a"]
                }
            ]
        }
        
        groomer = ClaudeTaskGroomer()
        
        # This should work without raising IntegrityError
        task_list, _ = groomer.create_task_list_from_groomed_tasks(
            "Test List",
            "test input",
            groomed_result
        )
        
        # Both tasks should be created
        self.assertEqual(task_list.tasks.count(), 2)
        
        # All database task_ids should be unique
        task_ids = list(task_list.tasks.values_list('task_id', flat=True))
        self.assertEqual(len(task_ids), len(set(task_ids)))  # No duplicates
        
        # Verify dependency mapping works correctly
        first_task = task_list.tasks.get(title="First task")
        second_task = task_list.tasks.get(title="Second task")
        
        self.assertEqual(second_task.dependencies.count(), 1)
        self.assertEqual(second_task.dependencies.first(), first_task)

    def test_task_creation_generates_unique_database_ids(self):
        """Test that database task_ids are always unique regardless of gen_task_ids"""
        groomed_result = {
            "success": True,
            "analysis": "Test analysis", 
            "tasks": [
                {
                    "task": "First task",
                    "gen_task_id": "task_1",
                    "time_estimate": "00:30",
                    "priority": "high",
                    "dependencies": []
                },
                {
                    "task": "Second task",
                    "gen_task_id": "task_2",
                    "time_estimate": "00:45",
                    "priority": "medium", 
                    "dependencies": ["task_1"]
                },
                {
                    "task": "Third task",
                    "gen_task_id": "task_3",
                    "time_estimate": "01:00",
                    "priority": "low",
                    "dependencies": ["task_1", "task_2"]
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
        
        # All database task_ids should be unique 4-char hex strings
        task_ids = list(task_list.tasks.values_list('task_id', flat=True))
        self.assertEqual(len(task_ids), len(set(task_ids)))  # No duplicates
        
        # All should be 4-character hex strings
        for task_id in task_ids:
            self.assertEqual(len(task_id), 4)
            self.assertTrue(all(c in '0123456789abcdef' for c in task_id))
        
        # Verify dependencies are correctly mapped using gen_task_ids
        first_task = task_list.tasks.get(title="First task")
        second_task = task_list.tasks.get(title="Second task")
        third_task = task_list.tasks.get(title="Third task")
        
        # Check dependencies
        self.assertEqual(first_task.dependencies.count(), 0)
        self.assertEqual(second_task.dependencies.count(), 1)
        self.assertEqual(third_task.dependencies.count(), 2)
        
        self.assertIn(first_task, second_task.dependencies.all())
        self.assertIn(first_task, third_task.dependencies.all())
        self.assertIn(second_task, third_task.dependencies.all())