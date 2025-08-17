#!/usr/bin/env python3
"""
Custom test runner script to handle AI testing flag
"""
import sys
import os
import django
from django.core.management import execute_from_command_line

def main():
    """Run tests with proper AI testing flag handling"""
    
    # Set up Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mindtimer.settings')
    
    # Check for AI testing flag
    ai_test_flag = '--AItest-ON'
    ai_test_enabled = ai_test_flag in sys.argv
    
    if ai_test_enabled:
        print("🔥 AI TESTING ENABLED - This will make real API calls and may incur costs!")
        print("💰 Make sure you have sufficient Claude API credits")
        print("-" * 60)
        # Remove the flag so Django doesn't see it
        sys.argv = [arg for arg in sys.argv if arg != ai_test_flag]
        # Set environment variable for tests to check
        os.environ['AI_TEST_ENABLED'] = 'true'
    else:
        print("🛡️  AI TESTING DISABLED - Integration and E2E tests will be skipped")
        print(f"💡 Use '{ai_test_flag}' flag to enable expensive AI tests")
        print("-" * 60)
    
    # Run Django test command
    if len(sys.argv) == 1:
        sys.argv.append('test')
    
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()