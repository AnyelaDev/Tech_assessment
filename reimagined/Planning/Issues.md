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

---
# Plan and dependencies comentary.

## Development Plan Overview

This plan follows a logical sequence that builds core functionality first, then adds quality and security layers, and finally polishes the application.

### Phase 1: Core Foundation (Issue 1 ✅ + Issue 6 ✅ + Issue 7 ✅)
**Goal:** Get the basic functionality working end-to-end

1. **Issue 1 (LLM Service) ✅ COMPLETED** - This critical blocker has been resolved with Claude Sonnet integration.
   - ✅ Replaced Hugging Face with working Claude API integration
   - ✅ Created comprehensive test suite with proper organization
   - ✅ This enabled all subsequent development work

2. **Issue 6 (Models) ✅ COMPLETED** - Enhanced data structure implemented
   - ✅ Task and TaskList models with proper validation
   - ✅ 4-byte hex task_id generation system
   - ✅ Circular dependency prevention
   - ✅ UI dependency display fixes
   - ✅ Comprehensive dependency management

3. **Issue 7 (Context Field) ✅ COMPLETED** - Enhanced AI processing capability
   - ✅ Optional context field in UI
   - ✅ Full integration with Claude API
   - ✅ Improved task grooming accuracy

**Dependencies:** All Phase 1 issues completed successfully.

### Phase 2: Quality & Architecture (Issues B-E)
**Goal:** Build additional reliability, security, and maintainable architecture

3. **Issue 8 (Tests) ✅ LARGELY COMPLETED** - Comprehensive test suite already implemented
   - ✅ Working Claude integration testing with cost protection
   - ✅ Unit/integration/e2e test structure in place
   - May need minor enhancements for specific edge cases

4. **Issue 9 (Configuration)** - Can be done in parallel with other work
   - Independent task that improves security
   - Makes the app more production-ready
   - No blocking dependencies

5. **Issue 10 (Service Architecture)** - Current architecture is solid but could be enhanced
   - Current ClaudeTaskGroomer service works well
   - Can be done incrementally while maintaining working code
   - Improves code quality and testability

6. **Issue 11 (CSRF Protection)** - Can be done anytime
   - Independent security improvement
   - Should be done before any major form submissions are implemented

### Phase 3: Polish & DevEx (Issues F-H)
**Goal:** Improve developer experience and code quality

7. **Issue 12 (Binary Cleanup)** - Housekeeping task, can be done anytime
   - No dependencies, purely maintenance
   - Low impact on functionality

8. **Issue 13 (CI/Pre-commit)** - Can be implemented now that tests are solid
   - ✅ Meaningful tests exist to run in CI
   - Improves development workflow but not functionality

9. **Issue 14 (Template/URL Naming)** - Pure refactoring, do last
   - No functional dependencies
   - Cosmetic improvements that don't affect core functionality

## Recommended Workflow

### Week 1: Core Functionality ✅ COMPLETED
- ✅ Day 1-2: LLM Integration (Issue 1) - Claude Sonnet implemented
- ✅ Day 3-4: Enhanced Models (Issue 6) - task_id, priority fields, validation added
- ✅ Day 5: Comprehensive testing and validation completed
- ✅ Day 6: Context field integration (Issue 7) - Enhanced AI processing

### Week 2: Additional Quality Foundation  
- Day 1-3: Enhanced Tests (Issue 8) - minor additions if needed
- Day 4: Configuration Management (Issue 9) 
- Day 5: CSRF Protection (Issue 11)

### Week 3: Architecture & Polish
- Day 1-2: Service Architecture (Issue 10)
- Day 3: CI/Pre-commit Setup (Issue 13)
- Day 4: Binary Cleanup (Issue 12)
- Day 5: Template/URL Polish (Issue 14)

## Critical Success Path
The minimum viable improvement path was: **Issue 1 → Issue 6 → Issue 7 → Issue 8**. ✅ **This has been completed** - we went from broken to working with comprehensive tests and enhanced AI processing. Everything else can be done iteratively as time permits.

## Risk Mitigation
- ✅ **Issue 1 risk resolved** - Claude API integration is stable and working
- ✅ **Issue 8 testing completed** - Comprehensive test suite with 20+ tests implemented
- **Issue 10 refactoring** - Do this incrementally to avoid breaking working code.