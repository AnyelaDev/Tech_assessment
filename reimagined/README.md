# MindTimer

Django application that converts free-form todo lists into structured schedules with AI assistance.

## Manual Testing

### Setup
```bash
source venv/bin/activate
python3 manage.py migrate
python3 manage.py runserver
```

### Database Testing
```bash
python3 manage.py shell

# Create test data
from tasks.models import TaskList, Task
task_list = TaskList.objects.create(name="Test List", raw_input="Clean kitchen\nBuy groceries")
task = Task.objects.create(title="Test Task", description="Description", estimated_duration=30, task_list=task_list)
print(f"Created: {task}")
```

### AI Service Testing
```bash
# First add your Hugging Face API key to .env file:
# HUGGINGFACE_API_KEY=your-actual-api-key-here

python3 manage.py shell

# Test AI integration (will fail without valid API key)
from tasks.services import TaskGroomer
try:
    groomer = TaskGroomer()
    result = groomer.process_todo("My Tasks", "Do laundry\nBuy milk\nClean room")
    print(f"AI processed {result.tasks.count()} tasks")
except ValueError as e:
    print(f"Expected error: {e}")
```

### UI Testing
```bash
# Start the development server
python3 manage.py runserver

# Open browser to http://127.0.0.1:8000/
# Test the form with sample data:
# - Task List Name: "Weekend Tasks"
# - Todo Text: "Do laundry\nBuy groceries\nClean kitchen\nCall mom"

# Expected behavior:
# - Without API key: Shows clear error message with setup instructions
# - With valid API key: Processes tasks and shows structured results
```

### Run Tests
```bash
DJANGO_SETTINGS_MODULE=mindtimer.settings python -m pytest tasks/tests/ -v
```