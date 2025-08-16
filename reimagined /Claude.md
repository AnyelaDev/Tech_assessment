# MindTimer - Project Context for Claude

## Project Overview
MindTimer is a Django-based web application that helps users convert free-form to-do lists into structured schedules with estimated times, dependencies, and opportunities for parallel execution. The app uses AI to process unstructured task lists and provides automated timers and notifications.

## Technology Stack
- **Backend**: Python + Django
- **Database**: SQLite (prototype) ’ PostgreSQL via Supabase (production)
- **Frontend**: Django templates with minimal HTML/CSS/JavaScript
- **AI Integration**: Hugging Face API (Mixtral-8x7B-Instruct-v0.1)

## Development Approach
- Test Driven Development (TDD)
- Start with core LLM integration functionality
- Keep UI simple and basic
- Color scheme managed centrally (no hardcoding)
- Avoid over-mocking in tests - focus on actual behavior

## Architecture Components
1. **Input Layer**: Django HTML forms for to-do list submission
2. **AI Processing**: Hugging Face API integration for task normalization
3. **Planning Algorithm**: Python module for schedule optimization
4. **Data Layer**: SQLite ’ PostgreSQL migration path
5. **UI Layer**: Django templates with JavaScript timers

## Commands to Run
- `python manage.py test` - Run test suite
- `python manage.py runserver` - Start development server
- `python manage.py migrate` - Apply database migrations
- `python manage.py collectstatic` - Collect static files

## Environment Variables
- `HUGGINGFACE_API_KEY` - Required for AI functionality
- `DEBUG` - Django debug mode
- `SECRET_KEY` - Django secret key
- `DATABASE_URL` - Database connection (when using PostgreSQL)

## Project Status
This is a reimagined version combining two previous projects with AI integration. Focus is on creating a functional MVP within 6 hours using Django's strengths while keeping the frontend simple.