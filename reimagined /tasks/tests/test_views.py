from django.test import TestCase, Client
from django.urls import reverse
from tasks.models import TaskList, Task


class TestHomeView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_view_renders_form(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'MindTimer')
        self.assertContains(response, '<form')
        self.assertContains(response, 'name="todo_text"')
        self.assertContains(response, 'name="task_list_name"')


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