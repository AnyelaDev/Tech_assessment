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
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your actual Claude API key

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

For detailed testing instructions including manual testing mode, see [TESTING.md](TESTING.md).

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

# Enable AI tests (⚠️ COSTS MONEY - requires `CLAUDE_API_KEY`)
python test_runner.py --AItest-ON

# Or using environment variable
`AI_TEST_ENABLED`=true python manage.py test

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

# View individual tasks with new ID system
for task in task_list.tasks.all():
    print(f"- {task.title} (ID: {task.task_id}, {task.priority}, {task.estimated_duration}min)")
    
# Check dependencies
for task in task_list.tasks.all():
    if task.dependencies.exists():
        deps = [dep.task_id for dep in task.dependencies.all()]
        print(f"  Dependencies: {deps}")
```

#### Database Testing
```bash
python manage.py shell

# Create test data with unique task_ids
from tasks.models import TaskList, Task
task_list = TaskList.objects.create(name="Test List", raw_input="Sample todo text")

# Task IDs are now auto-generated to ensure uniqueness
task1 = Task.objects.create(
    title="First Task",
    description="Task description", 
    priority="high",
    estimated_duration=60,
    task_list=task_list
)
print(f"Created: {task1} with ID {task1.task_id}")

task2 = Task.objects.create(
    title="Second Task",
    description="Depends on first task",
    priority="medium", 
    estimated_duration=30,
    task_list=task_list
)
task2.dependencies.add(task1)
print(f"Created: {task2} with ID {task2.task_id}, depends on {task1.task_id}")
```

## Architecture

### Models
- **TaskList**: Container for related tasks with original input text
- **Task**: Individual task with priority, time estimate, and dependencies
  - Unique 4-character hex `task_id` for database integrity
  - Many-to-many dependencies with circular dependency validation
  - Priority levels (high/medium/low) with validation
- **Schedule**: Optimization algorithms for task scheduling

### Services
- **ClaudeTaskGroomer**: AI service for todo text processing
  - **Two-Layer ID System**: Separates AI reference IDs (`gen_task_id`) from database IDs (`task_id`)
  - **Dependency Mapping**: Uses AI's `gen_task_id` for dependency relationships, then maps to database tasks
  - **Unique ID Generation**: Always generates unique 4-character hex database IDs
  - JSON response parsing with error handling
  - Time estimate conversion (hh:mm → minutes)

### Changelog

| Issue | Issue Name | What Was Fixed and Impact |
|-------|------------|---------------------------|
| 20 | Fix Unit Tests for Two-Layer ID System Implementation | Fixed failing unit tests by updating test fixtures and assertions to properly support the two-layer ID system. Cleaned up architecture by removing deprecated methods and backward compatibility clutter. Updated test fixtures to use `gen_task_id` for AI reference IDs, replaced direct ID lookups with title-based lookups, and added comprehensive validation for 4-hex database task_id format. Ensures clean separation between AI reference IDs and database integrity while maintaining full test coverage with all 12 unit tests passing. |
| 19 | Implement Pomodoro Timer Screen | Implemented complete Pomodoro timer functionality with configurable durations and comprehensive testing. Added new `/pomodoro/` route with full work/break cycle management, three distinct visual states (work/break/restart), real-time progress bars, timer controls (start/pause/stop/reset), and client-side JavaScript state management. Built comprehensive test suite with 18 passing tests covering URL routing, template rendering, and full user flow integration. Enhances executive function capabilities with focus session management. |
| 17 | Change Color in UI for Items with No Dependencies | Enhanced visual distinction for tasks without dependencies using TDD approach. Added `has_no_dependencies()` method to Task model, conditional CSS class application in templates, accessibility-compliant color scheme with high-contrast light green background and bright green left border, comprehensive test coverage for both dependencies and timeline views. Improves UX by making independent tasks easily identifiable. |
| 18 | Add Database Reset Button to Personal Assistance Page | Implemented convenient database reset functionality for development and testing. Added reset button to personal assistance page with confirmation dialog, backend endpoint to safely clear task/tasklist data while preserving auth data, comprehensive test coverage, and user feedback messages. |
| 15 | Fix UNIQUE constraint failed: tasks_task.task_id Database Error | Fixed IntegrityError crashes by implementing two-layer ID system (`gen_task_id` for AI references, `task_id` for database). Ensures robust dependency mapping and eliminates duplicate ID conflicts. Application now handles multiple task creation without database crashes. |
| 7 | Add Context Field for Enhanced AI Processing | Added optional context textarea field to improve AI task grooming accuracy. Connected context to TaskGroomer service and Claude API calls, included context in LLM prompt for better task analysis. |
| 6 | Define Minimal Models Explicitly | Enhanced Task and TaskList models with clear structure and validation. Fixed `task_id` generation with 4-byte hex format, added proper model validation with circular dependency prevention, and improved UI dependency display. |
| 1 | LLM Service | Initial AI integration for intelligent task breakdown and analysis. Implemented Claude Sonnet 3.5 integration with comprehensive testing, priority assignment, time estimation, task dependency management, and modern UI with cost protection system. |

### Key Features
- **Intelligent Parsing**: Claude breaks down complex todos into actionable tasks
- **Priority Assignment**: Automatic high/medium/low priority based on context
- **Time Estimates**: Realistic time predictions in hh:mm format
- **Dependency Management**: Task relationships for logical sequencing with robust ID mapping
- **Error Handling**: Graceful fallbacks for API failures and duplicate ID conflicts
- **Database Integrity**: Unique constraints with automatic collision resolution