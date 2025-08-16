from unittest.mock import patch, Mock
from django.test import TestCase
from django.conf import settings
from tasks.models import TaskList, Task
from tasks.services import TaskGroomer


class TestTaskGroomer(TestCase):
    def setUp(self):
        self.groomer = TaskGroomer()
        self.sample_todo = """
        Do laundry - wash and dry clothes
        Buy groceries for the week
        Clean the kitchen after cooking
        Call mom to check in
        """

    @patch('tasks.services.InferenceClient')
    def test_task_groomer_initialization(self, mock_client):
        groomer = TaskGroomer()
        mock_client.assert_called_once_with("mistralai/Mixtral-8x7B-Instruct-v0.1")
        self.assertIsNotNone(groomer.client)

    @patch('tasks.services.InferenceClient')
    def test_groom_tasks_returns_structured_data(self, mock_client):
        mock_response = """[
            {
                "title": "Do laundry",
                "description": "Wash and dry clothes",
                "estimated_duration": 120,
                "can_run_parallel": false,
                "dependencies": []
            },
            {
                "title": "Buy groceries", 
                "description": "Buy groceries for the week",
                "estimated_duration": 45,
                "can_run_parallel": true,
                "dependencies": []
            }
        ]"""
        
        mock_client_instance = Mock()
        mock_client_instance.text_generation.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        groomer = TaskGroomer()
        result = groomer.groom_tasks(self.sample_todo)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "Do laundry")
        self.assertEqual(result[0]["estimated_duration"], 120)
        self.assertEqual(result[1]["can_run_parallel"], True)

    @patch('tasks.services.InferenceClient')
    def test_groom_tasks_handles_api_error(self, mock_client):
        mock_client_instance = Mock()
        mock_client_instance.text_generation.side_effect = Exception("API Error")
        mock_client.return_value = mock_client_instance
        
        groomer = TaskGroomer()
        with self.assertRaises(Exception):
            groomer.groom_tasks(self.sample_todo)

    @patch('tasks.services.InferenceClient')
    def test_groom_tasks_handles_invalid_json(self, mock_client):
        mock_client_instance = Mock()
        mock_client_instance.text_generation.return_value = "Invalid JSON response"
        mock_client.return_value = mock_client_instance
        
        groomer = TaskGroomer()
        with self.assertRaises(Exception):
            groomer.groom_tasks(self.sample_todo)

    def test_create_task_list_from_groomed_tasks(self):
        groomed_tasks = [
            {
                "title": "Do laundry",
                "description": "Wash and dry clothes", 
                "estimated_duration": 120,
                "can_run_parallel": False,
                "dependencies": []
            },
            {
                "title": "Buy groceries",
                "description": "Buy groceries for the week",
                "estimated_duration": 45,
                "can_run_parallel": True,
                "dependencies": ["Do laundry"]
            }
        ]
        
        task_list = self.groomer.create_task_list_from_groomed_tasks(
            "Weekly Tasks", 
            self.sample_todo,
            groomed_tasks
        )
        
        self.assertEqual(task_list.name, "Weekly Tasks")
        self.assertEqual(task_list.raw_input, self.sample_todo)
        self.assertEqual(task_list.tasks.count(), 2)
        
        laundry_task = task_list.tasks.get(title="Do laundry")
        grocery_task = task_list.tasks.get(title="Buy groceries")
        
        self.assertEqual(laundry_task.estimated_duration, 120)
        self.assertFalse(laundry_task.can_run_parallel)
        self.assertEqual(grocery_task.estimated_duration, 45)
        self.assertTrue(grocery_task.can_run_parallel)

    @patch('tasks.services.InferenceClient')
    def test_process_todo_full_workflow(self, mock_client):
        mock_response = """[
            {
                "title": "Clean kitchen",
                "description": "Clean the kitchen after cooking",
                "estimated_duration": 30,
                "can_run_parallel": false,
                "dependencies": []
            }
        ]"""
        
        mock_client_instance = Mock()
        mock_client_instance.text_generation.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        groomer = TaskGroomer()
        task_list = groomer.process_todo("Kitchen Tasks", self.sample_todo)
        
        self.assertIsInstance(task_list, TaskList)
        self.assertEqual(task_list.name, "Kitchen Tasks")
        self.assertEqual(task_list.tasks.count(), 1)
        
        task = task_list.tasks.first()
        self.assertEqual(task.title, "Clean kitchen")
        self.assertEqual(task.estimated_duration, 30)