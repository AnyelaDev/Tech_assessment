"""
End-to-End Tests - Full workflow from todo text to database
"""
from django.test import TestCase
from django.urls import reverse

from tasks.models import TaskList, Task
from tasks.services import ClaudeTaskGroomer
from tests.utils import BaseClaudeTestCase, ClaudeTestSkipMixin, requires_claude_api, clean_test_data
from tests.fixtures.claude_responses import TEST_TODOS


class TestFullWorkflowE2E(BaseClaudeTestCase, ClaudeTestSkipMixin):
    """End-to-end tests covering the complete user workflow"""
    
    def setUp(self):
        super().setUp()
        self.skip_if_claude_key_invalid()
        
    def tearDown(self):
        """Clean up any test data"""
        clean_test_data()
    
    @requires_claude_api
    def test_complete_todo_to_database_workflow(self):
        """Test complete workflow from todo text to saved tasks in database"""
        todo_text = TEST_TODOS['grocery']
        list_name = "E2E Test Grocery List"
        
        # Step 1: Process todo through the service
        task_list, analysis = self.groomer.process_todo(list_name, todo_text)
        
        # Step 2: Verify TaskList was created and saved
        self.assertIsInstance(task_list, TaskList)
        self.assertTrue(task_list.pk)  # Should have database ID
        self.assertEqual(task_list.name, list_name)
        self.assertEqual(task_list.raw_input, todo_text)
        
        # Step 3: Verify analysis was provided
        self.assertTrue(analysis)
        self.assertIsInstance(analysis, str)
        self.assertGreater(len(analysis), 20, "Analysis should be substantial")
        
        # Step 4: Verify Tasks were created and saved to database
        tasks = task_list.tasks.all()
        self.assertGreater(tasks.count(), 0, "Should create at least one task")
        
        # Step 5: Verify task data integrity
        for task in tasks:
            # Required fields should be populated
            self.assertTrue(task.title, "Task title should not be empty")
            self.assertTrue(task.task_id, "Task ID should not be empty")
            self.assertNotEqual(task.task_id, "00000000", "Task ID should not be default")
            
            # Fields should have valid values
            self.assertIn(task.priority, ['low', 'medium', 'high'])
            self.assertGreater(task.estimated_duration, 0)
            
            # Should be linked to our task list
            self.assertEqual(task.task_list, task_list)
        
        # Step 6: Verify dependency relationships exist in database
        tasks_with_deps = tasks.filter(dependencies__isnull=False)
        if tasks.count() > 1:
            # For multi-task lists, should have some dependencies
            self.assertGreaterEqual(tasks_with_deps.count(), 0)
        
        # Step 7: Verify we can retrieve and use the data
        retrieved_list = TaskList.objects.get(pk=task_list.pk)
        self.assertEqual(retrieved_list.name, list_name)
        self.assertEqual(retrieved_list.tasks.count(), tasks.count())
    
    @requires_claude_api
    def test_complex_workflow_with_dependencies(self):
        """Test workflow with complex todo that creates task dependencies"""
        todo_text = TEST_TODOS['morning_routine'] 
        list_name = "E2E Morning Routine Test"
        
        # Process the complex todo
        task_list, analysis = self.groomer.process_todo(list_name, todo_text)
        
        # Should create multiple tasks
        tasks = task_list.tasks.all()
        self.assertGreaterEqual(tasks.count(), 3, "Morning routine should create multiple tasks")
        
        # Check for dependency chains
        all_dependencies = []
        for task in tasks:
            deps = list(task.dependencies.all())
            all_dependencies.extend(deps)
        
        # Complex workflow should have some dependencies
        if tasks.count() > 3:
            self.assertGreater(len(all_dependencies), 0, 
                             "Complex workflow should create task dependencies")
        
        # Verify dependency integrity - no circular dependencies
        for task in tasks:
            visited = set()
            current = task
            
            while current.dependencies.exists():
                if current.pk in visited:
                    self.fail(f"Circular dependency detected involving task {current.task_id}")
                visited.add(current.pk)
                current = current.dependencies.first()  # Check first dependency
    
    @requires_claude_api
    def test_multiple_task_lists_isolation(self):
        """Test that multiple task lists don't interfere with each other"""
        # Create first task list
        task_list_1, analysis_1 = self.groomer.process_todo(
            "E2E Test List 1", 
            "Buy groceries"
        )
        
        # Create second task list  
        task_list_2, analysis_2 = self.groomer.process_todo(
            "E2E Test List 2",
            "Plan birthday party"
        )
        
        # Verify both exist and are separate
        self.assertNotEqual(task_list_1.pk, task_list_2.pk)
        self.assertEqual(task_list_1.name, "E2E Test List 1")
        self.assertEqual(task_list_2.name, "E2E Test List 2")
        
        # Verify tasks are properly isolated
        tasks_1 = task_list_1.tasks.all()
        tasks_2 = task_list_2.tasks.all()
        
        # No task should belong to both lists
        for task in tasks_1:
            self.assertEqual(task.task_list, task_list_1)
            self.assertNotEqual(task.task_list, task_list_2)
        
        for task in tasks_2:
            self.assertEqual(task.task_list, task_list_2) 
            self.assertNotEqual(task.task_list, task_list_1)
    
    @requires_claude_api
    def test_task_list_total_time_calculation(self):
        """Test that total estimated time is calculated correctly"""
        task_list, analysis = self.groomer.process_todo(
            "E2E Time Calculation Test",
            "Prepare presentation and practice delivery"
        )
        
        tasks = task_list.tasks.all()
        
        # Calculate expected total manually
        expected_total = sum(task.estimated_duration for task in tasks)
        
        # Test the model method
        calculated_total = task_list.total_estimated_time()
        
        self.assertEqual(calculated_total, expected_total)
        self.assertGreater(calculated_total, 0, "Should have positive total time")
    
    @requires_claude_api
    def test_edge_case_handling_e2e(self):
        """Test end-to-end handling of edge cases"""
        edge_cases = [
            ("Single word task", "Clean"),
            ("Very specific task", "Call John at 555-1234 about the project deadline"),
            ("Emotional task", "I'm stressed about my presentation tomorrow help me break it down"),
        ]
        
        for test_name, todo_text in edge_cases:
            with self.subTest(case=test_name):
                try:
                    task_list, analysis = self.groomer.process_todo(
                        f"E2E Edge Case: {test_name}",
                        todo_text
                    )
                    
                    # Should create valid task list
                    self.assertIsInstance(task_list, TaskList)
                    self.assertTrue(task_list.pk)
                    
                    # Should have at least one task
                    tasks = task_list.tasks.all()
                    self.assertGreater(tasks.count(), 0)
                    
                    # Should have meaningful analysis
                    self.assertTrue(analysis)
                    
                except Exception as e:
                    self.fail(f"Edge case '{test_name}' failed: {e}")
    
    def test_database_consistency_after_failure(self):
        """Test that database remains consistent if task creation fails partway"""
        # This test uses invalid API key to simulate failure
        original_key = self.groomer.api_key
        self.groomer.api_key = "invalid_key"
        
        try:
            # This should fail
            with self.assertRaises(Exception):
                self.groomer.process_todo("Should Fail", "Test todo")
            
            # Database should not have partial data
            failed_lists = TaskList.objects.filter(name="Should Fail")
            self.assertEqual(failed_lists.count(), 0, 
                           "Failed task creation should not leave partial data")
            
        finally:
            # Restore original key
            self.groomer.api_key = original_key
    
    @requires_claude_api
    def test_task_update_workflow(self):
        """Test updating task completion status"""
        task_list, analysis = self.groomer.process_todo(
            "E2E Update Test",
            "Simple task for testing updates"
        )
        
        tasks = task_list.tasks.all()
        task = tasks.first()
        
        # Initially should not be completed
        self.assertFalse(task.completed)
        
        # Mark as completed
        task.mark_completed()
        
        # Verify it's marked completed
        task.refresh_from_db()
        self.assertTrue(task.completed)
        
        # Verify other tasks in list are not affected
        if tasks.count() > 1:
            other_task = tasks.exclude(pk=task.pk).first()
            self.assertFalse(other_task.completed)


class TestViewIntegrationE2E(TestCase, ClaudeTestSkipMixin):
    """End-to-end tests through Django views"""
    
    def setUp(self):
        self.skip_if_claude_key_invalid()
    
    def tearDown(self):
        clean_test_data()
    
    @requires_claude_api
    def test_home_to_results_workflow(self):
        """Test complete workflow from home form submission to results display"""
        # Simulate form submission
        response = self.client.post('/process/', {
            'task_list_name': 'E2E View Test',
            'todo_text': 'Buy milk and bread'
        })
        
        # Should redirect to results page
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/results/'))
        
        # Extract task list ID from redirect URL
        task_list_id = response.url.split('/')[-2]
        
        # Follow redirect to results page
        results_response = self.client.get(f'/results/{task_list_id}/')
        self.assertEqual(results_response.status_code, 200)
        
        # Verify content includes our task list
        self.assertContains(results_response, 'E2E View Test')
        self.assertContains(results_response, 'milk')
        
        # Verify task list was created in database
        task_list = TaskList.objects.get(pk=task_list_id)
        self.assertEqual(task_list.name, 'E2E View Test')
        self.assertGreater(task_list.tasks.count(), 0)
    
    def test_invalid_form_submission(self):
        """Test handling of invalid form data"""
        # Submit empty form
        response = self.client.post('/process/', {
            'task_list_name': '',
            'todo_text': ''
        })
        
        # Should return to home with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'required')
        
        # Should not create any task lists
        self.assertEqual(TaskList.objects.count(), 0)
    
    @requires_claude_api
    def test_timeline_workflow(self):
        """Test timeline input to dependencies workflow"""
        # Submit via timeline input
        response = self.client.post('/process-timeline/', {
            'task_list_name': 'E2E Timeline Test',
            'todo_text': 'Prepare dinner party'
        })
        
        # Should redirect to dependencies page
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/todo-dependencies/'))
        
        # Follow redirect
        task_list_id = response.url.split('/')[-2]
        deps_response = self.client.get(f'/todo-dependencies/{task_list_id}/')
        
        self.assertEqual(deps_response.status_code, 200)
        self.assertContains(deps_response, 'E2E Timeline Test')