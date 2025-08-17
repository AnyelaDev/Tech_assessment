from django.db import models
from django.core.exceptions import ValidationError
import secrets
import re


class TaskList(models.Model):
    name = models.CharField(max_length=200)
    raw_input = models.TextField(help_text="Original free-form todo list input")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def total_estimated_time(self):
        return sum(task.estimated_duration for task in self.tasks.all())


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    task_id = models.CharField(max_length=4, help_text="Unique 4-byte hexadecimal task identifier", unique=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    estimated_duration = models.PositiveIntegerField(help_text="Duration in minutes")
    completed = models.BooleanField(default=False)
    task_list = models.ForeignKey(TaskList, related_name='tasks', on_delete=models.CASCADE, null=True, blank=True)
    schedule_order = models.PositiveIntegerField(null=True, blank=True)
    dependencies = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='dependents')
    can_run_parallel = models.BooleanField(default=False, help_text="Can this task run in parallel with others?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.estimated_duration} min)"

    def mark_completed(self):
        self.completed = True
        self.save()

    def save(self, *args, **kwargs):
        if not self.task_id:
            self.task_id = self.generate_unique_task_id()
        super().save(*args, **kwargs)
    
    def generate_unique_task_id(self):
        """Generate a unique 4-byte hex task_id"""
        while True:
            task_id = secrets.token_hex(2)  # 2 bytes = 4 hex chars
            if not Task.objects.filter(task_id=task_id).exists():
                return task_id
    
    def clean(self):
        # Validate task_id format
        if self.task_id and not re.match(r'^[0-9a-fA-F]{4}$', self.task_id):
            raise ValidationError("task_id must be exactly 4 hexadecimal characters")
        
        # Validate duration
        if self.estimated_duration is not None and self.estimated_duration < 0:
            raise ValidationError("Duration cannot be negative")
        
        # Validate circular dependencies
        self._validate_no_circular_dependencies()
    
    def _validate_no_circular_dependencies(self):
        """Check for circular dependencies"""
        if not self.pk:
            return  # Skip validation for new objects
        
        visited = set()
        
        def has_circular_dependency(task, path):
            if task.pk in path:
                return True
            if task.pk in visited:
                return False
                
            visited.add(task.pk)
            path.add(task.pk)
            
            for dep in task.dependencies.all():
                if has_circular_dependency(dep, path):
                    return True
            
            path.remove(task.pk)
            return False
        
        if has_circular_dependency(self, set()):
            raise ValidationError("Circular dependency detected")
    
    def add_dependency(self, task_id_hex):
        """Add a dependency by task_id. Use '0000' to remove all dependencies."""
        if task_id_hex == "0000":
            self.dependencies.clear()
            return "All dependencies removed"
        
        # Validate hex format
        if not re.match(r'^[0-9a-fA-F]{4}$', task_id_hex):
            raise ValidationError("Invalid task_id format. Must be 4 hex characters.")
        
        # Check max dependencies limit
        if self.dependencies.count() >= 4:
            raise ValidationError("Maximum 4 dependencies allowed per task")
        
        # Find the target task
        try:
            target_task = Task.objects.get(task_id=task_id_hex.lower())
        except Task.DoesNotExist:
            raise ValidationError(f"Task with ID {task_id_hex} does not exist")
        
        # Check if already a dependency
        if target_task in self.dependencies.all():
            return f"Task {task_id_hex} is already a dependency"
        
        # Add dependency
        self.dependencies.add(target_task)
        return f"Added dependency: {target_task.task_id}"
    
    def get_dependency_ids(self):
        """Return list of dependent task IDs for UI display"""
        return [dep.task_id for dep in self.dependencies.all()]
    
    def get_dependency_display(self):
        """Return formatted string of dependencies for UI"""
        deps = self.get_dependency_ids()
        if not deps:
            return "None"
        return ", ".join(deps)


class Schedule(models.Model):
    OPTIMIZATION_CHOICES = [
        ('sequential', 'Sequential'),
        ('parallel', 'Parallel Optimization'),
        ('dependency', 'Dependency-Based'),
    ]
    
    task_list = models.ForeignKey(TaskList, related_name='schedules', on_delete=models.CASCADE)
    optimization_algorithm = models.CharField(max_length=20, choices=OPTIMIZATION_CHOICES, default='sequential')
    total_estimated_duration = models.PositiveIntegerField(null=True, blank=True, help_text="Total duration in minutes")
    parallel_blocks = models.JSONField(default=list, blank=True, help_text="Groups of tasks that can run in parallel")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Schedule for {self.task_list.name} ({self.optimization_algorithm})"

    def total_duration(self):
        return sum(task.estimated_duration for task in self.task_list.tasks.all())
