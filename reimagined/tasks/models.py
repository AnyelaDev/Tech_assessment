from django.db import models
from django.core.exceptions import ValidationError


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
    task_id = models.CharField(max_length=8, help_text="Unique hexadecimal task identifier", default="00000000")
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

    def clean(self):
        if self.estimated_duration is not None and self.estimated_duration < 0:
            raise ValidationError("Duration cannot be negative")


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
