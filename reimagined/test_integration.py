#!/usr/bin/env python3

import os
import django
import sys

# Set up Django environment
sys.path.append('/home/anveg/Development/Tech_assessment/reimagined')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mindtimer.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from tasks.models import TaskList, Task
from dotenv import load_dotenv

load_dotenv()

def test_todo_grooming_integration():
    """Test the full todo grooming workflow"""
    print("=== Testing Todo Grooming Integration ===")
    
    client = Client()
    
    # Clear any existing data
    Task.objects.all().delete()
    TaskList.objects.all().delete()
    
    # Test the form submission
    todo_data = {
        'todo_text': 'Do laundry\nBuy groceries\nClean kitchen',
        'context': 'Weekend tasks',
        'task_list_name': 'My Tasks'
    }
    
    print("📝 Submitting todo form...")
    response = client.post('/personal-assistance/executive-function/todo-timeline/process/', todo_data)
    
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 302:  # Redirect expected
        print(f"✅ Form submitted successfully, redirected to: {response.url}")
        
        # Check if TaskList was created
        task_lists = TaskList.objects.all()
        print(f"📊 Created {task_lists.count()} task list(s)")
        
        if task_lists.exists():
            task_list = task_lists.first()
            tasks = task_list.tasks.all()
            print(f"📋 Created {tasks.count()} task(s)")
            
            for task in tasks:
                print(f"  - {task.task_id}: {task.title} ({task.estimated_duration} min)")
                
            # Test the results page
            print("\n🔍 Testing results page...")
            results_response = client.get(f'/personal-assistance/executive-function/todo-timeline/dependencies/{task_list.id}/')
            print(f"Results page status: {results_response.status_code}")
            
            if results_response.status_code == 200:
                print("✅ Results page loads successfully")
                return True
            else:
                print("❌ Results page failed to load")
                return False
        else:
            print("❌ No TaskList created")
            return False
    else:
        print(f"❌ Form submission failed with status: {response.status_code}")
        print(f"Response content: {response.content.decode()[:500]}...")
        return False

def test_pomodoro_integration():
    """Test pomodoro page access"""
    print("\n=== Testing Pomodoro Integration ===")
    
    client = Client()
    response = client.get('/personal-assistance/executive-function/pomodoro/')
    
    print(f"Pomodoro page status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode()
        if "PomodoroTimer" in content and "Start Pomodoro" in content:
            print("✅ Pomodoro page loads with correct content")
            return True
        else:
            print("❌ Pomodoro page missing expected content")
            return False
    else:
        print("❌ Pomodoro page failed to load")
        return False

if __name__ == "__main__":
    success1 = test_todo_grooming_integration()
    success2 = test_pomodoro_integration()
    
    if success1 and success2:
        print("\n🎉 All integration tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some integration tests failed!")
        sys.exit(1)