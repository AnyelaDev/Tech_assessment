from django.test import TestCase
from django.core.exceptions import ValidationError
from tasks.models import Task, TaskList, Schedule


class TestTask(TestCase):
    def test_task_creation_with_required_fields(self):
        task = Task.objects.create(
            title="Test Task",
            description="A test task description",
            estimated_duration=30
        )
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.description, "A test task description")
        self.assertEqual(task.estimated_duration, 30)
        self.assertFalse(task.completed)

    def test_task_string_representation(self):
        task = Task.objects.create(
            title="Test Task",
            description="Description",
            estimated_duration=15
        )
        self.assertEqual(str(task), "Test Task (15 min)")

    def test_task_completion_toggle(self):
        task = Task.objects.create(
            title="Test Task",
            description="Description",
            estimated_duration=15
        )
        self.assertFalse(task.completed)
        task.mark_completed()
        self.assertTrue(task.completed)

    def test_task_duration_validation(self):
        with self.assertRaises(ValidationError):
            task = Task(
                title="Invalid Task",
                description="Description",
                estimated_duration=-5
            )
            task.full_clean()

    def test_task_has_no_dependencies_when_empty(self):
        task = Task.objects.create(
            title="Independent Task",
            description="A task with no dependencies",
            estimated_duration=30
        )
        self.assertTrue(task.has_no_dependencies())

    def test_task_has_no_dependencies_when_dependencies_exist(self):
        task1 = Task.objects.create(
            title="Dependent Task",
            description="A task that depends on another",
            estimated_duration=30
        )
        task2 = Task.objects.create(
            title="Dependency Task",
            description="A task that is a dependency",
            estimated_duration=15
        )
        task1.dependencies.add(task2)
        self.assertFalse(task1.has_no_dependencies())

    def test_task_has_no_dependencies_after_clearing(self):
        task1 = Task.objects.create(
            title="Task 1",
            description="Main task",
            estimated_duration=30
        )
        task2 = Task.objects.create(
            title="Task 2", 
            description="Dependency task",
            estimated_duration=15
        )
        task1.dependencies.add(task2)
        self.assertFalse(task1.has_no_dependencies())
        
        task1.dependencies.clear()
        self.assertTrue(task1.has_no_dependencies())


class TestTaskList(TestCase):
    def test_tasklist_creation(self):
        task_list = TaskList.objects.create(
            name="My Todo List",
            raw_input="Do laundry\nBuy groceries\nClean kitchen"
        )
        self.assertEqual(task_list.name, "My Todo List")
        self.assertEqual(task_list.raw_input, "Do laundry\nBuy groceries\nClean kitchen")

    def test_tasklist_string_representation(self):
        task_list = TaskList.objects.create(
            name="Weekly Tasks",
            raw_input="Some tasks"
        )
        self.assertEqual(str(task_list), "Weekly Tasks")

    def test_tasklist_total_estimated_time(self):
        task_list = TaskList.objects.create(
            name="Test List",
            raw_input="Tasks"
        )
        
        Task.objects.create(
            title="Task 1",
            description="First task",
            estimated_duration=30,
            task_list=task_list
        )
        Task.objects.create(
            title="Task 2", 
            description="Second task",
            estimated_duration=45,
            task_list=task_list
        )
        
        self.assertEqual(task_list.total_estimated_time(), 75)


class TestSchedule(TestCase):
    def test_schedule_creation(self):
        task_list = TaskList.objects.create(
            name="Test List",
            raw_input="Tasks to schedule"
        )
        
        schedule = Schedule.objects.create(
            task_list=task_list,
            optimization_algorithm="sequential"
        )
        
        self.assertEqual(schedule.task_list, task_list)
        self.assertEqual(schedule.optimization_algorithm, "sequential")
        self.assertIsNotNone(schedule.created_at)

    def test_schedule_string_representation(self):
        task_list = TaskList.objects.create(
            name="My Tasks",
            raw_input="Tasks"
        )
        
        schedule = Schedule.objects.create(
            task_list=task_list,
            optimization_algorithm="parallel"
        )
        
        self.assertEqual(str(schedule), "Schedule for My Tasks (parallel)")

    def test_schedule_total_duration(self):
        task_list = TaskList.objects.create(
            name="Test List",
            raw_input="Tasks"
        )
        
        schedule = Schedule.objects.create(
            task_list=task_list,
            optimization_algorithm="sequential"
        )
        
        Task.objects.create(
            title="Task 1",
            description="First",
            estimated_duration=20,
            task_list=task_list,
            schedule_order=1
        )
        Task.objects.create(
            title="Task 2",
            description="Second", 
            estimated_duration=35,
            task_list=task_list,
            schedule_order=2
        )
        
        self.assertEqual(schedule.total_duration(), 55)