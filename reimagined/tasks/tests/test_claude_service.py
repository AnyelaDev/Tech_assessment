"""
Basic Claude Service Tests - App-specific tests
"""
from django.test import TestCase
from tasks.services import ClaudeTaskGroomer
from tasks.models import TaskList, Task


class TestClaudeTaskGroomerBasic(TestCase):
    """Basic tests for ClaudeTaskGroomer service - app-level testing"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.groomer = ClaudeTaskGroomer()
    
    def test_service_initialization(self):
        """Test that ClaudeTaskGroomer can be initialized"""
        self.assertIsInstance(self.groomer, ClaudeTaskGroomer)
        self.assertTrue(hasattr(self.groomer, 'api_key'))
        self.assertTrue(hasattr(self.groomer, 'api_url'))
    
    def test_time_parsing_basic(self):
        """Basic test for time parsing functionality"""
        # Test valid format
        result = self.groomer.parse_time_estimate("01:30")
        self.assertEqual(result, 90)
        
        # Test invalid format defaults
        result = self.groomer.parse_time_estimate("invalid")
        self.assertEqual(result, 30)
    
    def test_task_model_has_required_fields(self):
        """Test that Task model has the fields we expect"""
        task_list = TaskList.objects.create(name="Test", raw_input="Test")
        
        # Test we can create a task with new fields
        task = Task.objects.create(
            title="Test Task",
            description="Test Description", 
            task_id="test123",
            priority="medium",
            estimated_duration=30,
            task_list=task_list
        )
        
        # Verify fields exist
        self.assertEqual(task.task_id, "test123")
        self.assertEqual(task.priority, "medium")
        self.assertTrue(hasattr(task, 'dependencies'))


# NOTE: Comprehensive tests have been moved to:
# - tests/unit/test_claude_service.py (unit tests with mocks)
# - tests/integration/test_claude_api.py (integration tests with real API)
# - tests/e2e/test_full_workflow.py (end-to-end workflow tests)