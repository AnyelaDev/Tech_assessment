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

## Issue #1 ✅ CLOSED
**Title:** LLM Service

**Description:** Initial AI integration for intelligent task breakdown and analysis.

**Resolution:** Successfully implemented Claude Sonnet 3.5 integration with comprehensive testing:
- [x] Claude API integration with error handling
- [x] Intelligent task breakdown from free-form text
- [x] Priority assignment and time estimation
- [x] Task dependency management
- [x] Modern UI with table display and analysis
- [x] Comprehensive test suite (unit/integration/e2e)
- [x] Database model enhancements (task_id, priority fields)
- [x] Cost protection system with --AItest-ON flag

**Impact:** High
**Priority:** High

## Issue 6
**Title:** Define Minimal Models Explicitly

**Description:** Task and TaskList models need clear structure and validation to support the core functionality.

**Acceptance criteria:**
- [ ] Create TaskList model (name, raw_input, created_at)
- [ ] Create Task model (task_list FK, title, estimated_minutes, can_overlap)
- [ ] Add proper model validation
- [ ] Consider depends_on M2M relationship for future

**Impact:** Medium
**Priority:** High


---
# List of issues not created yet. 

## Issue B
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

## Issue C
**Title:** Improve Configuration Management and Security

**Description:** Secrets are coupled to Django settings and need better management to avoid exposure.

**Acceptance criteria:**
- [ ] Add .env.example file with required keys
- [ ] Implement django-environ or pydantic-settings for config validation
- [ ] Ensure API keys are never printed or exposed
- [ ] Centralize configuration management

**Impact:** High
**Priority:** Medium

## Issue D
**Title:** Improve Service Architecture and Boundaries

**Description:** TaskGroomer service needs better separation of concerns and dependency injection.

**Acceptance criteria:**
- [ ] Make LLM client an explicit dependency (interface-based)
- [ ] Return pure data objects (dataclass) instead of Django models
- [ ] Implement mapping to models in view or repository layer
- [ ] Create clean service boundaries

**Impact:** Medium
**Priority:** Medium

## Issue E
**Title:** Add Security Headers and CSRF Protection

**Description:** As forms start mutating state, proper security measures need to be in place.

**Acceptance criteria:**
- [ ] Ensure CSRF tokens are present in templates
- [ ] Verify Django security headers are properly configured
- [ ] Test form security measures

**Impact:** Medium
**Priority:** Medium

## Issue F
**Title:** Remove Binary Artifacts from Git History

**Description:** SQLite DB and potentially large PNG mockups are committed to repository history.

**Acceptance criteria:**
- [ ] Ensure db.sqlite3 stays in .gitignore
- [ ] Consider moving large mockups to Git LFS if needed
- [ ] Clean up repository to keep it lightweight

**Impact:** Medium
**Priority:** Low

## Issue G
**Title:** Add Pre-commit Hooks and CI

**Description:** Repository lacks automated code quality checks and continuous integration.

**Acceptance criteria:**
- [ ] Add pre-commit hooks with ruff, black, isort
- [ ] Create GitHub Actions workflow for pytest
- [ ] Set up matrix testing for Python 3.10/3.11
- [ ] Ensure tests run in CI environment

**Impact:** Low
**Priority:** Low

## Issue H
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

### Phase 1: Core Foundation (Issue 1 ✅ + Issue 6)
**Goal:** Get the basic functionality working end-to-end

1. **Issue 1 (LLM Service) ✅ COMPLETED** - This critical blocker has been resolved with Claude Sonnet integration.
   - ✅ Replaced Hugging Face with working Claude API integration
   - ✅ Created comprehensive test suite with proper organization
   - ✅ This enabled all subsequent development work

2. **Issue 6 (Models)** - Define enhanced data structure for remaining features
   - TaskList and Task models may need further enhancements
   - Required for any additional features beyond current implementation
   - Current models are functional but could be extended

**Dependencies:** Issue 1 is completed. Issue 6 can be developed independently.

### Phase 2: Quality & Architecture (Issues B-E)
**Goal:** Build additional reliability, security, and maintainable architecture

3. **Issue B (Tests) ✅ LARGELY COMPLETED** - Comprehensive test suite already implemented
   - ✅ Working Claude integration testing with cost protection
   - ✅ Unit/integration/e2e test structure in place
   - May need minor enhancements for specific edge cases

4. **Issue C (Configuration)** - Can be done in parallel with other work
   - Independent task that improves security
   - Makes the app more production-ready
   - No blocking dependencies

5. **Issue D (Service Architecture)** - Current architecture is solid but could be enhanced
   - Current ClaudeTaskGroomer service works well
   - Can be done incrementally while maintaining working code
   - Improves code quality and testability

6. **Issue E (CSRF Protection)** - Can be done anytime
   - Independent security improvement
   - Should be done before any major form submissions are implemented

### Phase 3: Polish & DevEx (Issues F-H)
**Goal:** Improve developer experience and code quality

7. **Issue F (Binary Cleanup)** - Housekeeping task, can be done anytime
   - No dependencies, purely maintenance
   - Low impact on functionality

8. **Issue G (CI/Pre-commit)** - Can be implemented now that tests are solid
   - ✅ Meaningful tests exist to run in CI
   - Improves development workflow but not functionality

9. **Issue H (Template/URL Naming)** - Pure refactoring, do last
   - No functional dependencies
   - Cosmetic improvements that don't affect core functionality

## Recommended Workflow

### Week 1: Core Functionality ✅ COMPLETED
- ✅ Day 1-2: LLM Integration (Issue 1) - Claude Sonnet implemented
- ✅ Day 3-4: Enhanced Models - task_id, priority fields added
- ✅ Day 5: Comprehensive testing and validation completed

### Week 2: Additional Quality Foundation  
- Day 1-3: Enhanced Tests (Issue B) - minor additions if needed
- Day 4: Configuration Management (Issue C) 
- Day 5: CSRF Protection (Issue E)

### Week 3: Architecture & Polish
- Day 1-2: Service Architecture (Issue D)
- Day 3: CI/Pre-commit Setup (Issue G)
- Day 4: Binary Cleanup (Issue F)
- Day 5: Template/URL Polish (Issue H)

## Critical Success Path
The minimum viable improvement path was: **Issue 1 → Issue 6 → Issue B**. ✅ **This has been completed** - we went from broken to working with comprehensive tests. Everything else can be done iteratively as time permits.

## Risk Mitigation
- ✅ **Issue 1 risk resolved** - Claude API integration is stable and working
- ✅ **Issue B testing completed** - Comprehensive test suite with 20+ tests implemented
- **Issue D refactoring** - Do this incrementally to avoid breaking working code.