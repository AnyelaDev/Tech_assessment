# MindTimer

Django application that converts free-form todo lists into structured, actionable tasks with Claude Sonnet AI assistance.

## Features

- **AI-Powered Task Breakdown**: Uses Claude Sonnet to intelligently break down vague todos into specific, actionable tasks
- **Priority Management**: Automatically assigns priorities (high/medium/low) based on task importance
- **Time Estimation**: Provides realistic time estimates for each task in hh:mm format
- **Dependency Tracking**: Identifies and manages task dependencies for logical sequencing
- **Modern UI**: Clean, responsive interface with table-based task display
- **Comprehensive Analysis**: Shows Claude's reasoning for task breakdown decisions

## Quick Start

### Prerequisites
- Python 3.10+
- Django 5.2.5
- Claude API key from [Anthropic Console](https://console.anthropic.com/)

### Setup
```bash
cd "/home/anveg/Development/Tech_assessment/reimagined"

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install django python-dotenv requests

# Configure Claude API key
echo "CLAUDE_API_KEY=your_claude_api_key_here" >> .env

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

### Usage
1. Visit http://127.0.0.1:8000/
2. Navigate to Personal Assistance → Executive Function → ToDo Timeline
3. Enter your todo text (e.g., "Prepare for job interview tomorrow")
4. View the structured breakdown with priorities, time estimates, and dependencies

## Testing

### Test Structure
The project uses a comprehensive TDD approach with organized test categories:

```
tests/
├── unit/           # Fast tests with mocked APIs (12 tests, ~0.02s)
├── integration/    # Real Claude API tests (requires API key)
├── e2e/           # End-to-end workflow tests (full user flow)
├── fixtures/      # Shared test data and mock responses
└── utils.py       # Test utilities and helpers
```

### Running Tests

**⚠️ Important**: AI integration tests are expensive and disabled by default to prevent accidental API charges.

```bash
# Safe tests (unit tests only, no API calls)
python manage.py test tests.unit
python manage.py test tasks.tests

# All tests (skips expensive AI tests)
python manage.py test

# Enable AI tests (⚠️ COSTS MONEY - requires CLAUDE_API_KEY)
python test_runner.py --AItest-ON

# Or using environment variable
AI_TEST_ENABLED=true python manage.py test

# Run specific expensive test categories
python test_runner.py --AItest-ON tests.integration
python test_runner.py --AItest-ON tests.e2e
```

**Cost Protection:**
- Integration and E2E tests are skipped by default
- Use `--AItest-ON` flag only when you want to test real Claude API integration
- Unit tests (12 tests, ~0.02s) always run and are free

### Test Coverage
- ✅ Claude API integration (success/error cases)
- ✅ JSON response parsing and validation
- ✅ Time estimate conversion (hh:mm → minutes)
- ✅ Task creation with priorities and dependencies
- ✅ Database model integration
- ✅ Full workflow testing from todo text to saved tasks
- ✅ Django view integration
- ✅ Error handling and edge cases

### Manual Testing

#### Claude Service Testing
```bash
python manage.py shell

# Test Claude integration
from tasks.services import ClaudeTaskGroomer
groomer = ClaudeTaskGroomer()

# Process a simple todo
task_list, analysis = groomer.process_todo(
    "Test List", 
    "Prepare for job interview tomorrow and buy a new shirt"
)

print(f"Created {task_list.tasks.count()} tasks")
print(f"Analysis: {analysis}")

# View individual tasks
for task in task_list.tasks.all():
    print(f"- {task.title} ({task.priority}, {task.estimated_duration}min)")
```

#### Database Testing
```bash
python manage.py shell

# Create test data with new fields
from tasks.models import TaskList, Task
task_list = TaskList.objects.create(name="Test List", raw_input="Sample todo text")
task = Task.objects.create(
    title="Test Task",
    description="Task description",
    task_id="a101",
    priority="high",
    estimated_duration=60,
    task_list=task_list
)
print(f"Created: {task} with priority {task.priority}")
```

## Architecture

### Models
- **TaskList**: Container for related tasks with original input text
- **Task**: Individual task with priority, time estimate, and dependencies
- **Schedule**: Optimization algorithms for task scheduling

### Services
- **ClaudeTaskGroomer**: AI service for todo text processing
  - JSON response parsing
  - Time estimate conversion
  - Dependency relationship mapping

### Key Features
- **Intelligent Parsing**: Claude breaks down complex todos into actionable tasks
- **Priority Assignment**: Automatic high/medium/low priority based on context
- **Time Estimates**: Realistic time predictions in hh:mm format
- **Dependency Management**: Task relationships for logical sequencing
- **Error Handling**: Graceful fallbacks for API failures