from django.test import TestCase, Client
from django.urls import reverse
from tasks.models import TaskList, Task
import json


class TestHomeView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_view_redirects_to_personal_assistance(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/personal-assistance/')


class TestResultsView(TestCase):
    def setUp(self):
        self.client = Client()
        self.task_list = TaskList.objects.create(
            name="Weekly Tasks",
            raw_input="Do laundry\nBuy groceries\nClean kitchen"
        )
        Task.objects.create(
            title="Do laundry",
            description="Wash and dry clothes", 
            estimated_duration=120,
            task_list=self.task_list
        )
        Task.objects.create(
            title="Buy groceries",
            description="Buy food for the week",
            estimated_duration=45,
            task_list=self.task_list,
            can_run_parallel=True
        )

    def test_results_view_displays_task_details(self):
        response = self.client.get(f'/results/{self.task_list.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Weekly Tasks')
        self.assertContains(response, 'Do laundry')
        self.assertContains(response, 'Buy groceries')
        self.assertContains(response, '120 min')
        self.assertContains(response, '45 min')

    def test_results_view_shows_total_estimated_time(self):
        response = self.client.get(f'/results/{self.task_list.id}/')
        self.assertContains(response, 'Total time: 165 minutes')

    def test_results_view_shows_parallel_tasks(self):
        response = self.client.get(f'/results/{self.task_list.id}/')
        self.assertContains(response, 'Can run in parallel')

    def test_results_view_invalid_task_list_id_returns_404(self):
        response = self.client.get('/results/999/')
        self.assertEqual(response.status_code, 404)


class TestProcessTodoView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_process_todo_requires_post_method(self):
        response = self.client.get('/process/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    def test_process_todo_with_empty_form_data_shows_error(self):
        response = self.client.post('/process/', {
            'task_list_name': '',
            'todo_text': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error')

    def test_process_todo_form_validation_requires_both_fields(self):
        response = self.client.post('/process/', {
            'task_list_name': 'My Tasks',
            'todo_text': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'required')


class TestNavigationViews(TestCase):
    def setUp(self):
        self.client = Client()

    def test_personal_assistance_landing_view(self):
        response = self.client.get('/personal-assistance/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Personal Assistance')
        self.assertContains(response, 'Executive function')
        self.assertContains(response, 'Emotions Management')
        self.assertContains(response, 'Habits')

    def test_executive_function_view(self):
        response = self.client.get('/personal-assistance/executive-function/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Executive Function')
        self.assertContains(response, 'ToDo Timeline')
        self.assertContains(response, 'Pomodoro')
        self.assertContains(response, 'Routines')

    def test_todo_timeline_input_view(self):
        response = self.client.get('/personal-assistance/executive-function/todo-timeline/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'To-Do List')
        self.assertContains(response, 'write your to do list')
        self.assertContains(response, 'Groom my list')

    def test_todo_dependencies_view_with_valid_task_list(self):
        task_list = TaskList.objects.create(
            name="Test Tasks",
            raw_input="Do laundry\nBuy groceries"
        )
        Task.objects.create(
            title="Do laundry",
            description="Wash and dry clothes",
            estimated_duration=120,
            task_list=task_list
        )
        
        response = self.client.get(f'/personal-assistance/executive-function/todo-timeline/dependencies/{task_list.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Times and Dependencies')
        self.assertContains(response, 'Establish ToDos')
        self.assertContains(response, 'Do laundry')
        self.assertContains(response, 'Time:')
        self.assertContains(response, 'Dependencies:')

    def test_todo_dependencies_view_invalid_id_returns_404(self):
        response = self.client.get('/personal-assistance/executive-function/todo-timeline/dependencies/999/')
        self.assertEqual(response.status_code, 404)

    def test_timeline_execution_view_with_valid_task_list(self):
        task_list = TaskList.objects.create(
            name="Test Tasks",
            raw_input="Do laundry\nBuy groceries"
        )
        Task.objects.create(
            title="Do laundry",
            description="Wash and dry clothes",
            estimated_duration=120,
            task_list=task_list
        )
        Task.objects.create(
            title="Buy groceries",
            description="Shop for food",
            estimated_duration=45,
            task_list=task_list,
            can_run_parallel=True
        )
        
        response = self.client.get(f'/personal-assistance/executive-function/todo-timeline/execute/{task_list.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Timeline')
        self.assertContains(response, 'Now')
        self.assertContains(response, 'in parallel:')
        self.assertContains(response, 'Home')
        self.assertContains(response, 'Back')

    def test_timeline_execution_view_invalid_id_returns_404(self):
        response = self.client.get('/personal-assistance/executive-function/todo-timeline/execute/999/')
        self.assertEqual(response.status_code, 404)

    def test_navigation_breadcrumbs_context(self):
        response = self.client.get('/personal-assistance/executive-function/')
        self.assertEqual(response.status_code, 200)
        # Test that proper context is passed for navigation

    def test_executive_function_has_back_button(self):
        response = self.client.get('/personal-assistance/executive-function/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/personal-assistance/"')
        self.assertContains(response, 'Back')

    def test_todo_timeline_input_has_back_button(self):
        response = self.client.get('/personal-assistance/executive-function/todo-timeline/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/personal-assistance/executive-function/"')
        self.assertContains(response, 'Back')

    def test_dependencies_view_has_back_button(self):
        task_list = TaskList.objects.create(
            name="Test Tasks",
            raw_input="Do laundry\nBuy groceries"
        )
        response = self.client.get(f'/personal-assistance/executive-function/todo-timeline/dependencies/{task_list.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/personal-assistance/executive-function/todo-timeline/"')
        self.assertContains(response, 'Back')

    def test_timeline_execution_already_has_back_button(self):
        task_list = TaskList.objects.create(
            name="Test Tasks",
            raw_input="Do laundry\nBuy groceries"
        )
        response = self.client.get(f'/personal-assistance/executive-function/todo-timeline/execute/{task_list.id}/')
        self.assertEqual(response.status_code, 200)
        # Timeline execution already has back and home buttons from our implementation
        self.assertContains(response, 'Back')
        self.assertContains(response, 'Home')

    def test_personal_assistance_landing_no_back_button(self):
        response = self.client.get('/personal-assistance/')
        self.assertEqual(response.status_code, 200)
        # Landing page should NOT have a back button
        self.assertNotContains(response, 'Back')

    def test_root_url_redirects_to_personal_assistance(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/personal-assistance/')


class TestResetDatabaseView(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create test data
        self.task_list_1 = TaskList.objects.create(
            name="Test Tasks 1",
            raw_input="Do laundry\nBuy groceries"
        )
        self.task_list_2 = TaskList.objects.create(
            name="Test Tasks 2",
            raw_input="Clean kitchen\nWash dishes"
        )
        
        self.task_1 = Task.objects.create(
            title="Do laundry",
            description="Wash and dry clothes",
            estimated_duration=120,
            task_list=self.task_list_1
        )
        self.task_2 = Task.objects.create(
            title="Buy groceries",
            description="Shop for food",
            estimated_duration=45,
            task_list=self.task_list_1,
            can_run_parallel=True
        )
        self.task_3 = Task.objects.create(
            title="Clean kitchen",
            description="Deep clean the kitchen",
            estimated_duration=60,
            task_list=self.task_list_2
        )

    def test_reset_database_requires_post_method(self):
        response = self.client.get('/personal-assistance/reset-database/')
        self.assertEqual(response.status_code, 405)  # Method not allowed

    def test_reset_database_successful_reset(self):
        # Verify initial data exists
        self.assertEqual(TaskList.objects.count(), 2)
        self.assertEqual(Task.objects.count(), 3)
        
        # Make POST request to reset endpoint
        response = self.client.post('/personal-assistance/reset-database/')
        
        # Verify successful response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('Database reset successfully', response_data['message'])
        self.assertIn('Deleted 3 tasks and 2 task lists', response_data['message'])
        
        # Verify all data is deleted
        self.assertEqual(TaskList.objects.count(), 0)
        self.assertEqual(Task.objects.count(), 0)

    def test_reset_database_empty_database(self):
        # Clear existing data first
        TaskList.objects.all().delete()
        Task.objects.all().delete()
        
        # Verify database is empty
        self.assertEqual(TaskList.objects.count(), 0)
        self.assertEqual(Task.objects.count(), 0)
        
        # Make POST request to reset endpoint
        response = self.client.post('/personal-assistance/reset-database/')
        
        # Should still return success
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('Deleted 0 tasks and 0 task lists', response_data['message'])

    def test_reset_database_returns_json_response(self):
        response = self.client.post('/personal-assistance/reset-database/')
        
        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = json.loads(response.content)
        
        # Verify expected JSON structure
        self.assertIn('success', response_data)
        self.assertIn('message', response_data)
        self.assertIsInstance(response_data['success'], bool)