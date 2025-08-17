# MindTimer - Project Context for Claude

## Project Overview
MindTimer is a Django-based web application that helps users convert free-form to-do lists into structured, actionable tasks using Claude Sonnet AI. The app intelligently breaks down vague todos, assigns priorities, provides time estimates, and manages task dependencies.

## Current Implementation Status ✅
- **Claude Sonnet Integration**: Fully implemented and working
- **Task Model Enhancement**: Added `task_id`, `priority` fields with migrations
- **Modern UI**: Table-based task display with priority badges and dependency visualization
- **Comprehensive Testing**: 20+ tests across unit/integration/e2e categories
- **TDD Approach**: Complete test coverage with proper organization

## Technology Stack
- **Backend**: Python + Django
- **Database**: SQLite (prototype) � PostgreSQL via Supabase (production)
- **Frontend**: Django templates with minimal HTML/CSS/JavaScript
- **AI Integration**: Claude Sonnet 3.5 (claude-3-5-sonnet-20241022) via Anthropic API

## Development Approach
- Test Driven Development (TDD)
- Start with core LLM integration functionality
- Keep UI simple and basic
- Color scheme managed centrally (no hardcoding)
- Avoid over-mocking in tests - focus on actual behavior

## Documentation Conventions
- **Changelog Order**: Ordered by completion date (most recent first), NOT by issue number
- **Issue Numbers**: Are identifiers only, not chronological order
- **README Updates**: Always update changelog when completing issues

## Architecture Components
1. **Input Layer**: Django HTML forms for to-do list submission
2. **AI Processing**: Claude Sonnet API integration for intelligent task breakdown
3. **Planning Algorithm**: Python module for schedule optimization
4. **Data Layer**: SQLite � PostgreSQL migration path
5. **UI Layer**: Django templates with JavaScript timers

## Commands to Run
- `python manage.py test` - Run all tests (skips expensive AI tests)
- `python manage.py test tests.unit` - Fast unit tests (0.02s, always safe)
- `python test_runner.py --AItest-ON` - ⚠️ Enable expensive AI tests (costs money!)
- `python test_runner.py --AItest-ON tests.integration` - Real Claude API tests
- `python test_runner.py --AItest-ON tests.e2e` - End-to-end workflow tests
- `python manage.py runserver` - Start development server
- `python manage.py migrate` - Apply database migrations
- `python manage.py shell` - Interactive testing shell

## Cost Protection
**AI tests are disabled by default** to prevent accidental API charges. The `--AItest-ON` flag must be explicitly used to enable expensive integration and end-to-end tests that make real Claude API calls.

## Environment Variables
- `CLAUDE_API_KEY` - Required for Claude Sonnet AI functionality (from https://console.anthropic.com/)
- `HUGGINGFACE_API_KEY` - Legacy (removed)
- `HUGGINGFACE_MODEL` - Legacy (removed)
- `DEBUG` - Django debug mode
- `SECRET_KEY` - Django secret key
- `DATABASE_URL` - Database connection (when using PostgreSQL)

## Project Status
**COMPLETED**: Claude Sonnet integration is fully functional with comprehensive testing.

### What Works
- ✅ Claude API integration with error handling
- ✅ Intelligent task breakdown from free-form text
- ✅ Priority assignment and time estimation
- ✅ Task dependency management
- ✅ Modern UI with table display and analysis
- ✅ Comprehensive test suite (unit/integration/e2e)
- ✅ Database migrations and model enhancements

### Test Coverage
- **Unit Tests**: 12 tests with mocked APIs (0.018s runtime)
- **Integration Tests**: Real Claude API testing
- **E2E Tests**: Complete workflow validation
- **Fixtures**: Shared test data and utilities

### Usage Example
```python
# Process a todo with Claude
from tasks.services import ClaudeTaskGroomer
groomer = ClaudeTaskGroomer()
task_list, analysis = groomer.process_todo(
    "Interview Prep",
    "Prepare for job interview tomorrow and buy new shirt"
)
print(f"Created {task_list.tasks.count()} tasks with analysis")
```

This implementation provides a solid foundation for AI-powered task management with room for future enhancements like scheduling optimization and notification systems.