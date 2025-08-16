# Issues Template

To create issue{{ 
    Title:  Title

    Description: Short description

    Acceptance criteria: to do list style in markdown

    Impact: high or low
    Priority: High, medium, low, or cosmetic
}}

---
# Issues in GitHub

## Issue #5
**Title:** Fix Hugging Face Integration - Use Remote API Instead of Local Model

**Description:** Current HF integration tries to download and run models locally instead of using remote inference API, causing performance issues or failures.

**Acceptance criteria:** 
- [ ] Replace `transformers.pipeline()` with `huggingface_hub.InferenceClient`
- [ ] Create `HFClient` wrapper class for remote inference
- [ ] Inject HFClient into TaskGroomer for testability
- [ ] Remove transformers dependency from request path

**Impact:** High
**Priority:** High

---
# List of issues not created yet. 

## Issue 2
**Title:** Define Minimal Models Explicitly

**Description:** Task and TaskList models need clear structure and validation to support the core functionality.

**Acceptance criteria:**
- [ ] Create TaskList model (name, raw_input, created_at)
- [ ] Create Task model (task_list FK, title, estimated_minutes, can_overlap)
- [ ] Add proper model validation
- [ ] Consider depends_on M2M relationship for future

**Impact:** Medium
**Priority:** High

## Issue 3
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

## Issue 4
**Title:** Improve Configuration Management and Security

**Description:** Secrets are coupled to Django settings and need better management to avoid exposure.

**Acceptance criteria:**
- [ ] Add .env.example file with required keys
- [ ] Implement django-environ or pydantic-settings for config validation
- [ ] Ensure API keys are never printed or exposed
- [ ] Centralize configuration management

**Impact:** High
**Priority:** Medium

## Issue 5
**Title:** Improve Service Architecture and Boundaries

**Description:** TaskGroomer service needs better separation of concerns and dependency injection.

**Acceptance criteria:**
- [ ] Make LLM client an explicit dependency (interface-based)
- [ ] Return pure data objects (dataclass) instead of Django models
- [ ] Implement mapping to models in view or repository layer
- [ ] Create clean service boundaries

**Impact:** Medium
**Priority:** Medium

## Issue 6
**Title:** Add Security Headers and CSRF Protection

**Description:** As forms start mutating state, proper security measures need to be in place.

**Acceptance criteria:**
- [ ] Ensure CSRF tokens are present in templates
- [ ] Verify Django security headers are properly configured
- [ ] Test form security measures

**Impact:** Medium
**Priority:** Medium

## Issue 7
**Title:** Remove Binary Artifacts from Git History

**Description:** SQLite DB and potentially large PNG mockups are committed to repository history.

**Acceptance criteria:**
- [ ] Ensure db.sqlite3 stays in .gitignore
- [ ] Consider moving large mockups to Git LFS if needed
- [ ] Clean up repository to keep it lightweight

**Impact:** Medium
**Priority:** Low

## Issue 8
**Title:** Add Pre-commit Hooks and CI

**Description:** Repository lacks automated code quality checks and continuous integration.

**Acceptance criteria:**
- [ ] Add pre-commit hooks with ruff, black, isort
- [ ] Create GitHub Actions workflow for pytest
- [ ] Set up matrix testing for Python 3.10/3.11
- [ ] Ensure tests run in CI environment

**Impact:** Low
**Priority:** Low

## Issue 9
**Title:** Improve Template Naming and URL Design

**Description:** Templates and URLs could follow more consistent patterns.

**Acceptance criteria:**
- [ ] Consider consistent prefixes for templates (tasks_*.html)
- [ ] Make routes more REST-ish where possible
- [ ] Improve URL pattern consistency

**Impact:** Low
**Priority:** Cosmetic

---
# Plan and dependencies comentary.

## Development Plan Overview

This plan follows a logical sequence that builds core functionality first, then adds quality and security layers, and finally polishes the application.

### Phase 1: Core Foundation (Issues 1-2)
**Goal:** Get the basic functionality working end-to-end

1. **Start with Issue 1 (HF Integration)** - This is the critical blocker that prevents the app from working at all. Must be fixed before meaningful testing can happen.
   - Replace local model loading with remote API calls
   - Create testable HFClient wrapper
   - This enables all other development work

2. **Follow with Issue 2 (Models)** - Define the data structure that everything else depends on
   - TaskList and Task models form the backbone of the application
   - Required before writing meaningful tests or service improvements
   - No other dependencies block this work

**Dependencies:** Issue 1 must be completed before Issue 2 can be properly tested, but Issue 2 can be developed in parallel.

### Phase 2: Quality & Architecture (Issues 3-6)
**Goal:** Build reliability, security, and maintainable architecture

3. **Issue 3 (Tests)** - Can start once Issues 1-2 are complete
   - Depends on working HF integration (Issue 1) for integration tests
   - Depends on proper models (Issue 2) for model tests
   - Tests will validate that the foundation works correctly

4. **Issue 4 (Configuration)** - Can be done in parallel with testing
   - Independent task that improves security
   - Makes the app more production-ready
   - No blocking dependencies

5. **Issue 5 (Service Architecture)** - Should wait until tests are in place
   - Depends on Issue 3 (tests) to ensure refactoring doesn't break functionality
   - Can be done incrementally while maintaining working code
   - Improves code quality and testability

6. **Issue 6 (CSRF Protection)** - Can be done anytime after Phase 1
   - Independent security improvement
   - Should be done before any major form submissions are implemented

### Phase 3: Polish & DevEx (Issues 7-9)
**Goal:** Improve developer experience and code quality

7. **Issue 7 (Binary Cleanup)** - Housekeeping task, can be done anytime
   - No dependencies, purely maintenance
   - Low impact on functionality

8. **Issue 8 (CI/Pre-commit)** - Should wait until tests are solid (Issue 3)
   - Depends on having meaningful tests to run in CI
   - Improves development workflow but not functionality

9. **Issue 9 (Template/URL Naming)** - Pure refactoring, do last
   - No functional dependencies
   - Cosmetic improvements that don't affect core functionality

## Recommended Workflow

### Week 1: Core Functionality
- Day 1-2: Fix HF Integration (Issue 1) 
- Day 3-4: Define Models (Issue 2)
- Day 5: Manual testing and validation

### Week 2: Quality Foundation  
- Day 1-3: Implement Tests (Issue 3)
- Day 4: Configuration Management (Issue 4) 
- Day 5: CSRF Protection (Issue 6)

### Week 3: Architecture & Polish
- Day 1-2: Service Architecture (Issue 5)
- Day 3: CI/Pre-commit Setup (Issue 8)
- Day 4: Binary Cleanup (Issue 7)
- Day 5: Template/URL Polish (Issue 9)

## Critical Success Path
The minimum viable improvement path is: **Issue 1 → Issue 2 → Issue 3**. This gets you from broken to working with tests. Everything else can be done iteratively as time permits.

## Risk Mitigation
- **Issue 1 is high risk** - HF API changes could cause delays. Have a backup plan to mock the service entirely if needed.
- **Issue 3 testing** - Start simple with just one test per category, then expand.
- **Issue 5 refactoring** - Do this incrementally to avoid breaking working code.