# Test Suite Documentation

## Test Structure

The test suite is organized into logical categories for better maintainability:

```
tests/
├── unit/                       # Fast tests with mocked dependencies
│   └── test_claude_service.py
├── integration/                # Tests requiring real API calls  
│   └── test_claude_api.py
├── e2e/                        # End-to-end workflow tests
│   └── test_full_workflow.py
├── fixtures/                   # Shared test data
│   └── claude_responses.py
└── utils.py                    # Test utilities and helpers

tasks/tests/                    # App-specific tests
├── test_models.py
├── test_views.py
└── test_services.py            # Basic service tests
```

## Running Tests

### All Tests
```bash
python manage.py test
```

### By Category
```bash
# Fast unit tests (mocked APIs)
python manage.py test tests.unit

# Integration tests (require CLAUDE_API_KEY)  
python manage.py test tests.integration

# End-to-end tests (full workflow)
python manage.py test tests.e2e

# App-specific tests
python manage.py test tasks.tests
```

### Individual Test Files
```bash
python manage.py test tests.unit.test_claude_service
python manage.py test tests.integration.test_claude_api
python manage.py test tests.e2e.test_full_workflow
```

### With Pytest (if installed)
```bash
# All tests
pytest

# By markers
pytest -m unit      # Fast unit tests
pytest -m integration  # Integration tests
pytest -m e2e       # End-to-end tests
```

## Test Types

### Unit Tests (`tests/unit/`)
- **Purpose**: Fast tests with mocked dependencies
- **Requirements**: None (all external calls mocked)
- **Speed**: Very fast (< 1 second per test)
- **Use**: Development, CI/CD pipelines

### Integration Tests (`tests/integration/`)  
- **Purpose**: Test real Claude API integration
- **Requirements**: Valid `CLAUDE_API_KEY` environment variable
- **Speed**: Moderate (2-10 seconds per test)
- **Use**: Validating API integration works

### End-to-End Tests (`tests/e2e/`)
- **Purpose**: Full workflow from todo input to database
- **Requirements**: Valid `CLAUDE_API_KEY` environment variable
- **Speed**: Slower (5-15 seconds per test)
- **Use**: Validating complete user workflows

## Environment Setup

### For Unit Tests Only
No special setup required - all dependencies are mocked.

### For Integration and E2E Tests
1. Set `CLAUDE_API_KEY` in your `.env` file:
   ```
   CLAUDE_API_KEY=your_actual_api_key_here
   ```

2. Tests will be skipped if the API key is not configured or appears to be a placeholder.

## Test Fixtures and Utilities

### Shared Fixtures (`tests/fixtures/claude_responses.py`)
- Mock Claude API responses for consistent testing
- Test todo inputs for different scenarios
- Helper functions for creating mock HTTP responses

### Test Utilities (`tests/utils.py`)
- `BaseClaudeTestCase`: Common test setup
- `ClaudeTestSkipMixin`: Skip tests when API key unavailable  
- `@requires_claude_api`: Decorator for integration tests
- Helper assertions for validating Claude responses

## Best Practices

1. **Use appropriate test type**: Unit for logic, integration for APIs, e2e for workflows
2. **Mock external dependencies** in unit tests for speed and reliability
3. **Keep tests focused**: One concept per test method
4. **Use descriptive test names** that explain what is being tested
5. **Clean up test data** in tearDown methods for e2e tests

## Test Coverage

The test suite covers:
- ✅ Claude API integration (success/error cases)
- ✅ JSON response parsing and validation
- ✅ Time estimate parsing (hh:mm → minutes)
- ✅ Task creation with priorities and dependencies
- ✅ Database model integration
- ✅ Full workflow from todo text to saved tasks
- ✅ Django view integration
- ✅ Error handling and edge cases

## Troubleshooting

### Tests Skip with "CLAUDE_API_KEY not configured"
- Set a valid Claude API key in your `.env` file
- Get an API key from https://console.anthropic.com/

### Tests Fail with API Errors
- Check your API key is valid and has sufficient credits
- Check network connectivity
- Some tests may be rate-limited - run fewer tests concurrently

### Import Errors
- Ensure you're in the correct directory (`reimagined/`)
- Activate your virtual environment: `source .venv/bin/activate`
- Install dependencies: `pip install django python-dotenv requests`