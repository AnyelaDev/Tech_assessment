"""
Integration Tests for Claude API - Real API calls (requires valid API key)
"""
from django.test import TestCase
from django.conf import settings

from tasks.services import ClaudeTaskGroomer
from tests.utils import BaseClaudeTestCase, ClaudeTestSkipMixin, requires_claude_api
from tests.fixtures.claude_responses import TEST_TODOS


class TestClaudeAPIIntegration(BaseClaudeTestCase, ClaudeTestSkipMixin):
    """Integration tests that make real Claude API calls"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        super().setUp()
        self.skip_if_ai_testing_disabled()
        self.skip_if_claude_key_invalid()
    
    @requires_claude_api
    def test_simple_api_call(self):
        """Test simple Claude API call with real service"""
        result = self.groomer.groom_tasks(TEST_TODOS['simple'])
        
        # Should succeed with valid API key
        self.assertTrue(result.get('success'), f"API call failed: {result.get('error')}")
        self.assertIn('analysis', result)
        self.assertIn('tasks', result)
        self.assertIsInstance(result['tasks'], list)
        self.assertGreater(len(result['tasks']), 0)
        
        # Verify response structure
        self.assert_claude_response_structure(result)
    
    @requires_claude_api
    def test_complex_todo_breakdown(self):
        """Test complex todo breakdown with real API"""
        result = self.groomer.groom_tasks(TEST_TODOS['complex'])
        
        self.assertTrue(result.get('success'))
        
        # Should break complex todo into multiple tasks
        tasks = result.get('tasks', [])
        self.assertGreaterEqual(len(tasks), 3, "Complex todo should create multiple tasks")
        
        # Should have meaningful analysis
        analysis = result.get('analysis', '')
        self.assertTrue(analysis)
        self.assertGreater(len(analysis), 50, "Analysis should be substantial")
        
        # Should have mixed priorities for complex tasks
        priority_counts = self.count_tasks_by_priority(tasks)
        total_high_medium = priority_counts['high'] + priority_counts['medium']
        self.assertGreater(total_high_medium, 0, "Should prioritize important tasks")
        
        # Verify all task structures
        for task in tasks:
            self.assert_task_structure(task)
    
    @requires_claude_api  
    def test_grocery_todo_with_dependencies(self):
        """Test grocery todo that should create dependency chains"""
        result = self.groomer.groom_tasks(TEST_TODOS['grocery'])
        
        self.assertTrue(result.get('success'))
        
        tasks = result.get('tasks', [])
        self.assertGreaterEqual(len(tasks), 2)
        
        # Look for logical dependencies (shopping before cooking)
        tasks_with_deps = [t for t in tasks if t.get('dependencies')]
        
        # Should have some dependencies for logical sequencing
        if len(tasks) > 2:
            self.assertGreater(len(tasks_with_deps), 0, 
                             "Multi-step grocery tasks should have dependencies")
    
    @requires_claude_api
    def test_morning_routine_breakdown(self):
        """Test complex morning routine breakdown"""
        result = self.groomer.groom_tasks(TEST_TODOS['morning_routine'])
        
        self.assertTrue(result.get('success'))
        
        tasks = result.get('tasks', [])
        self.assertGreaterEqual(len(tasks), 5, "Morning routine should create many tasks")
        
        # Should have time-sensitive tasks marked as high priority
        high_priority_tasks = [t for t in tasks if t.get('priority') == 'high']
        self.assertGreater(len(high_priority_tasks), 0, "Time-sensitive tasks should be high priority")
        
        # Should have realistic time estimates
        for task in tasks:
            time_estimate = task.get('time_estimate', '00:00')
            # Parse to minutes and check reasonableness
            parts = time_estimate.split(':')
            if len(parts) == 2:
                hours, minutes = int(parts[0]), int(parts[1])
                total_minutes = hours * 60 + minutes
                self.assertGreater(total_minutes, 0, "Tasks should have positive time estimates")
                self.assertLessEqual(total_minutes, 180, "Individual tasks should be <= 3 hours")
    
    @requires_claude_api
    def test_empty_todo_handling(self):
        """Test how Claude handles empty or minimal input"""
        result = self.groomer.groom_tasks(TEST_TODOS['empty'])
        
        # May succeed or fail gracefully - either is acceptable
        if result.get('success'):
            # If it succeeds, should have some response
            self.assertIsInstance(result.get('tasks', []), list)
        else:
            # If it fails, should have error message
            self.assertIn('error', result)
    
    @requires_claude_api
    def test_api_response_consistency(self):
        """Test that API responses are consistent and well-formed"""
        test_cases = [
            ("Buy milk", "simple task"),
            ("Plan birthday party and send invitations", "multi-step task"),
            ("Learn Python programming", "broad goal")
        ]
        
        for todo_text, description in test_cases:
            with self.subTest(case=description):
                result = self.groomer.groom_tasks(todo_text)
                
                if result.get('success'):
                    # Verify consistent response structure
                    self.assert_claude_response_structure(result)
                    
                    # Verify all tasks have unique task_ids
                    task_ids = [t.get('task_id') for t in result.get('tasks', [])]
                    self.assertEqual(len(task_ids), len(set(task_ids)), 
                                   "All task IDs should be unique")
                    
                    # Verify task_ids are reasonable format
                    for task_id in task_ids:
                        self.assertRegex(task_id, r'^[a-z0-9]{3,8}$',
                                       f"Task ID '{task_id}' should be reasonable format")
    
    @requires_claude_api
    def test_api_error_recovery(self):
        """Test API behavior with potentially problematic inputs"""
        problematic_inputs = [
            "a" * 10,  # Very short
            "task " * 100,  # Repetitive
            "URGENT!!! HELP!!! EMERGENCY!!!"  # Excessive punctuation
        ]
        
        for problem_input in problematic_inputs:
            with self.subTest(input=problem_input[:20] + "..."):
                result = self.groomer.groom_tasks(problem_input)
                
                # Should either succeed gracefully or fail with clear error
                if not result.get('success'):
                    self.assertIn('error', result)
                    self.assertTrue(result['error'])  # Error message should not be empty
                else:
                    # If successful, should still have valid structure
                    self.assert_claude_response_structure(result)


class TestClaudeAPILimits(BaseClaudeTestCase, ClaudeTestSkipMixin):
    """Test Claude API behavior at various limits"""
    
    def setUp(self):
        super().setUp()
        self.skip_if_ai_testing_disabled()
        self.skip_if_claude_key_invalid()
    
    @requires_claude_api
    def test_reasonable_response_times(self):
        """Test that API responses come back in reasonable time"""
        import time
        
        start_time = time.time()
        result = self.groomer.groom_tasks("Quick test task")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # API should respond within reasonable time (30 seconds max)
        self.assertLess(response_time, 30.0, 
                       f"API took {response_time:.2f} seconds - too slow")
        
        # If successful, response should have content
        if result.get('success'):
            self.assertTrue(result.get('analysis'))
            self.assertTrue(result.get('tasks'))
    
    @requires_claude_api
    def test_task_count_reasonableness(self):
        """Test that Claude creates reasonable number of tasks"""
        test_cases = [
            ("Buy bread", 1, 3),  # Simple task: 1-3 tasks expected
            ("Plan vacation to Japan", 3, 15),  # Complex task: 3-15 tasks expected
            ("Organize home office", 2, 10)  # Medium task: 2-10 tasks expected
        ]
        
        for todo, min_tasks, max_tasks in test_cases:
            with self.subTest(todo=todo):
                result = self.groomer.groom_tasks(todo)
                
                if result.get('success'):
                    task_count = len(result.get('tasks', []))
                    self.assertGreaterEqual(task_count, min_tasks,
                                          f"'{todo}' should create at least {min_tasks} tasks")
                    self.assertLessEqual(task_count, max_tasks,
                                       f"'{todo}' should create at most {max_tasks} tasks")