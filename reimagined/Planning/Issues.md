# Issues Template

To create issue{{ 
    Title:  Title

    Description: Short description

    Acceptance criteria: to do list style in markdown

    Impact: high or low
    Priority: High, medium, low, or cosmetic
}}

---
---
# List of issues not created yet. 

## Issue 8
**Title:** Implement Meaningful Tests (Currently Mostly Placeholders)

**Description:** Tests exist as scaffolding but lack meaningful assertions and behavior validation.

**Acceptance criteria:**
- [ ] Unit test for TaskGroomer.process_todo() with stubbed LLM response
- [ ] Model tests for TaskList and Task validation
- [ ] Integration test for views with error handling
- [ ] Routing/smoke tests for URL resolution
- [ ] Edge case tests (empty lines, malformed durations, duplicates)

**Impact:** High
**Priority:** Medium

## Issue 9
**Title:** Improve Configuration Management and Security

**Description:** Secrets are coupled to Django settings and need better management to avoid exposure.

**Acceptance criteria:**
- [ ] Add .env.example file with required keys
- [ ] Implement django-environ or pydantic-settings for config validation
- [ ] Ensure API keys are never printed or exposed
- [ ] Centralize configuration management

**Impact:** High
**Priority:** Medium

## Issue 10
**Title:** Improve Service Architecture and Boundaries

**Description:** TaskGroomer service needs better separation of concerns and dependency injection.

**Acceptance criteria:**
- [ ] Make LLM client an explicit dependency (interface-based)
- [ ] Return pure data objects (dataclass) instead of Django models
- [ ] Implement mapping to models in view or repository layer
- [ ] Create clean service boundaries

**Impact:** Medium
**Priority:** Medium

## Issue 11
**Title:** Add Security Headers and CSRF Protection

**Description:** As forms start mutating state, proper security measures need to be in place.

**Acceptance criteria:**
- [ ] Ensure CSRF tokens are present in templates
- [ ] Verify Django security headers are properly configured
- [ ] Test form security measures

**Impact:** Medium
**Priority:** Medium

## Issue 12
**Title:** Remove Binary Artifacts from Git History

**Description:** SQLite DB and potentially large PNG mockups are committed to repository history.

**Acceptance criteria:**
- [ ] Ensure db.sqlite3 stays in .gitignore
- [ ] Consider moving large mockups to Git LFS if needed
- [ ] Clean up repository to keep it lightweight

**Impact:** Medium
**Priority:** Low

## Issue 13
**Title:** Add Pre-commit Hooks and CI

**Description:** Repository lacks automated code quality checks and continuous integration.

**Acceptance criteria:**
- [ ] Add pre-commit hooks with ruff, black, isort
- [ ] Create GitHub Actions workflow for pytest
- [ ] Set up matrix testing for Python 3.10/3.11
- [ ] Ensure tests run in CI environment

**Impact:** Low
**Priority:** Low

## Issue 14
**Title:** Improve Template Naming and URL Design

**Description:** Templates and URLs could follow more consistent patterns.

**Acceptance criteria:**
- [ ] Consider consistent prefixes for templates (tasks_*.html)
- [ ] Make routes more REST-ish where possible
- [ ] Improve URL pattern consistency

**Impact:** Low
**Priority:** Cosmetic

## Issue 16
**Title:** Simple Lists to JSON - No Deep Analysis, Simpler Models

**Description:** Simplify the AI processing workflow to convert simple lists directly to JSON without complex analysis. Consider using simpler models for basic task creation scenarios.

**Acceptance criteria:**
- [ ] Create lightweight JSON conversion endpoint for simple list inputs
- [ ] Implement basic task parsing without deep AI analysis
- [ ] Evaluate if simpler models can be used for basic scenarios
- [ ] Add option to bypass complex AI processing for simple lists
- [ ] Maintain compatibility with existing complex processing workflow

**Impact:** Medium
**Priority:** Medium

## Issue 20
**Title:** Fix Unit Tests for Two-Layer ID System Implementation

**Description:** Unit tests are failing because they expect the old single-ID behavior where database task_id matched AI's task_id directly. The two-layer ID system (Issue 15 fix) correctly separates AI reference IDs (gen_task_id) from database IDs (task_id), but tests need to be updated to reflect this architecture.

**Acceptance criteria:**
- [ ] Update test fixtures to use `gen_task_id` instead of `task_id` for AI reference IDs
- [ ] Modify unit tests to expect unique 4-hex database task_ids instead of AI reference IDs
- [ ] Ensure tests validate that AI gen_task_id mapping works correctly for dependencies
- [ ] Update test assertions to check both gen_task_id mapping and database task_id uniqueness
- [ ] Maintain test coverage for the complete two-layer ID system functionality
- [ ] Verify all unit tests pass while preserving integration test functionality
- [ ] Ensure backward compatibility with existing data and real Claude API responses

**Impact:** High
**Priority:** Medium

