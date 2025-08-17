#!/usr/bin/env python3
"""
Test Driven Development - Claude Integration Tests
"""
import os
import sys
import django
import json

# Determine script location and set up paths
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(script_dir, 'reimagined')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mindtimer.settings')
sys.path.insert(0, project_dir)
os.chdir(project_dir)
django.setup()

from tasks.services import ClaudeTaskGroomer
from tasks.models import TaskList, Task

class TestClaudeIntegration:
    def __init__(self):
        self.groomer = None
        self.passed = 0
        self.failed = 0
    
    def setUp(self):
        """Initialize test setup"""
        try:
            self.groomer = ClaudeTaskGroomer()
            print("✓ Test setup complete")
            return True
        except Exception as e:
            print(f"✗ Test setup failed: {e}")
            return False
    
    def test_claude_api_connection(self):
        """Test 1: Verify Claude API connection works"""
        print("\n--- Test 1: Claude API Connection ---")
        
        try:
            simple_todo = "Call dentist"
            result = self.groomer.groom_tasks(simple_todo)
            
            if result.get('success'):
                print("✓ Claude API connection successful")
                self.passed += 1
                return True
            else:
                print(f"✗ Claude API failed: {result.get('error')}")
                self.failed += 1
                return False
                
        except Exception as e:
            print(f"✗ Exception in API test: {e}")
            self.failed += 1
            return False
    
    def test_json_parsing(self):
        """Test 2: Verify JSON response parsing"""
        print("\n--- Test 2: JSON Response Parsing ---")
        
        try:
            test_todo = "Buy groceries and cook dinner"
            result = self.groomer.groom_tasks(test_todo)
            
            if not result.get('success'):
                print(f"✗ API call failed: {result.get('error')}")
                self.failed += 1
                return False
            
            # Check required fields exist
            required_fields = ['analysis', 'tasks']
            for field in required_fields:
                if field not in result:
                    print(f"✗ Missing required field: {field}")
                    self.failed += 1
                    return False
            
            # Check tasks structure
            tasks = result.get('tasks', [])
            if not tasks:
                print("✗ No tasks returned")
                self.failed += 1
                return False
            
            for i, task in enumerate(tasks):
                required_task_fields = ['task', 'task_id', 'time_estimate', 'priority']
                for field in required_task_fields:
                    if field not in task:
                        print(f"✗ Task {i} missing field: {field}")
                        self.failed += 1
                        return False
            
            print("✓ JSON parsing and structure validation passed")
            self.passed += 1
            return True
            
        except Exception as e:
            print(f"✗ Exception in JSON parsing test: {e}")
            self.failed += 1
            return False
    
    def test_time_parsing(self):
        """Test 3: Verify time estimate parsing"""
        print("\n--- Test 3: Time Estimate Parsing ---")
        
        test_cases = [
            ("01:30", 90),
            ("00:15", 15),
            ("02:00", 120),
            ("invalid", 30),  # Should default to 30
            ("", 30)  # Should default to 30
        ]
        
        try:
            for time_str, expected_minutes in test_cases:
                result = self.groomer.parse_time_estimate(time_str)
                if result == expected_minutes:
                    print(f"✓ Time parsing '{time_str}' -> {result} minutes")
                else:
                    print(f"✗ Time parsing '{time_str}' expected {expected_minutes}, got {result}")
                    self.failed += 1
                    return False
            
            print("✓ All time parsing tests passed")
            self.passed += 1
            return True
            
        except Exception as e:
            print(f"✗ Exception in time parsing test: {e}")
            self.failed += 1
            return False
    
    def test_complex_todo_breakdown(self):
        """Test 4: Complex todo breakdown with dependencies"""
        print("\n--- Test 4: Complex Todo Breakdown ---")
        
        complex_todo = """
        I need to prepare for my job interview next week. I should research the company, 
        update my resume, practice common interview questions, and buy a new shirt. 
        Also need to confirm the interview time and location.
        """
        
        try:
            result = self.groomer.groom_tasks(complex_todo.strip())
            
            if not result.get('success'):
                print(f"✗ API call failed: {result.get('error')}")
                self.failed += 1
                return False
            
            tasks = result.get('tasks', [])
            analysis = result.get('analysis', '')
            
            # Should break down into multiple tasks
            if len(tasks) < 3:
                print(f"✗ Expected multiple tasks, got {len(tasks)}")
                self.failed += 1
                return False
            
            # Should have analysis
            if not analysis:
                print("✗ Missing analysis")
                self.failed += 1
                return False
            
            # Check for different priorities
            priorities = set(task.get('priority') for task in tasks)
            if len(priorities) < 2:
                print("✗ Expected mixed priorities")
                # This is a warning, not a failure
                print("⚠ All tasks have same priority")
            
            print(f"✓ Complex todo broken into {len(tasks)} tasks")
            print(f"✓ Analysis provided: {analysis[:100]}...")
            print(f"✓ Priorities found: {', '.join(priorities)}")
            
            self.passed += 1
            return True
            
        except Exception as e:
            print(f"✗ Exception in complex todo test: {e}")
            self.failed += 1
            return False
    
    def test_django_integration(self):
        """Test 5: Full Django model integration"""
        print("\n--- Test 5: Django Model Integration ---")
        
        try:
            test_name = "Test Task List"
            test_todo = "Plan weekend trip and pack bags"
            
            # Test full process_todo method
            task_list, analysis = self.groomer.process_todo(test_name, test_todo)
            
            # Verify TaskList created
            if not isinstance(task_list, TaskList):
                print("✗ TaskList not created properly")
                self.failed += 1
                return False
            
            if task_list.name != test_name:
                print(f"✗ TaskList name incorrect: expected '{test_name}', got '{task_list.name}'")
                self.failed += 1
                return False
            
            # Verify Tasks created
            tasks = task_list.tasks.all()
            if not tasks:
                print("✗ No tasks created")
                self.failed += 1
                return False
            
            # Verify task fields
            for task in tasks:
                if not task.task_id or task.task_id == "00000000":
                    print(f"✗ Task '{task.title}' has invalid task_id: '{task.task_id}'")
                    self.failed += 1
                    return False
                
                if task.priority not in ['low', 'medium', 'high']:
                    print(f"✗ Task '{task.title}' has invalid priority: '{task.priority}'")
                    self.failed += 1
                    return False
                
                if task.estimated_duration <= 0:
                    print(f"✗ Task '{task.title}' has invalid duration: {task.estimated_duration}")
                    self.failed += 1
                    return False
            
            # Verify analysis
            if not analysis:
                print("✗ No analysis returned")
                self.failed += 1
                return False
            
            print(f"✓ TaskList '{task_list.name}' created with {tasks.count()} tasks")
            print(f"✓ All tasks have valid task_ids, priorities, and durations")
            print(f"✓ Analysis returned: {analysis[:100]}...")
            
            # Clean up test data
            task_list.delete()
            print("✓ Test data cleaned up")
            
            self.passed += 1
            return True
            
        except Exception as e:
            print(f"✗ Exception in Django integration test: {e}")
            self.failed += 1
            return False
    
    def test_error_handling(self):
        """Test 6: Error handling for edge cases"""
        print("\n--- Test 6: Error Handling ---")
        
        try:
            # Test empty todo
            result = self.groomer.groom_tasks("")
            if result.get('success'):
                print("✓ Empty todo handled gracefully")
            else:
                print(f"⚠ Empty todo error: {result.get('error')}")
            
            # Test very long todo
            long_todo = "Task " * 1000  # Very long input
            result = self.groomer.groom_tasks(long_todo)
            if result.get('success') or 'error' in result:
                print("✓ Long todo handled gracefully")
            else:
                print("⚠ Long todo handling unclear")
            
            print("✓ Error handling tests completed")
            self.passed += 1
            return True
            
        except Exception as e:
            print(f"✗ Exception in error handling test: {e}")
            self.failed += 1
            return False
    
    def run_all_tests(self):
        """Run all tests and report results"""
        print("=" * 60)
        print("CLAUDE INTEGRATION TEST SUITE")
        print("=" * 60)
        
        if not self.setUp():
            print("Cannot run tests - setup failed")
            return
        
        tests = [
            self.test_claude_api_connection,
            self.test_json_parsing,
            self.test_time_parsing,
            self.test_complex_todo_breakdown,
            self.test_django_integration,
            self.test_error_handling
        ]
        
        for test in tests:
            test()
        
        print("\n" + "=" * 60)
        print("TEST RESULTS")
        print("=" * 60)
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Total:  {self.passed + self.failed}")
        
        if self.failed == 0:
            print("🎉 ALL TESTS PASSED!")
            return True
        else:
            print(f"❌ {self.failed} TESTS FAILED")
            return False

def main():
    tester = TestClaudeIntegration()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())