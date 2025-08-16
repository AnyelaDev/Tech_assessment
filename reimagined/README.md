# MindTimer

Django application that converts free-form todo lists into structured schedules with AI assistance.

## Manual Testing

### Setup
```bash
cd "/home/anveg/Development/Tech_assessment/reimagined"
./venv/bin/python manage.py migrate
./venv/bin/python manage.py runserver
```

Alternative if virtual environment activation works:
```bash
source venv/bin/activate
python3 manage.py migrate
python3 manage.py runserver
```

### Database Testing
```bash
./venv/bin/python manage.py shell

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

./venv/bin/python manage.py shell

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
./venv/bin/python manage.py runserver

# Open browser to http://127.0.0.1:8000/
# Navigate through the new UI:
# 1. Personal Assistance landing page
# 2. Executive Function → ToDo Timeline
# 3. Test the form with sample data:
#    - Todo Text: "Do laundry\nBuy groceries\nClean kitchen\nCall mom"
#    - Task List Name field is marked as mock/development only

# Expected behavior:
# - Navigation flows through all screens with back buttons
# - Without API key: Shows error message (AI integration on separate branch)
# - All UI elements match the mockup designs
```

### Run Tests
```bash
DJANGO_SETTINGS_MODULE=mindtimer.settings ./venv/bin/python -m pytest tasks/tests/ -v
```