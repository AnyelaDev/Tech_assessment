"""
Shared Claude API response fixtures for testing
"""
import json

# Sample successful Claude API responses
SIMPLE_TODO_RESPONSE = {
    "analysis": "Simple task breakdown with basic prioritization.",
    "tasks": [
        {
            "task": "Call dentist to schedule appointment",
            "gen_task_id": "a101",
            "time_estimate": "00:05",
            "dependencies": [],
            "priority": "medium"
        }
    ]
}

COMPLEX_TODO_RESPONSE = {
    "analysis": "Complex task breakdown with dependencies and realistic time estimates. Tasks are organized by priority and logical sequence.",
    "tasks": [
        {
            "task": "Research company background and values",
            "gen_task_id": "a101", 
            "time_estimate": "01:00",
            "dependencies": [],
            "priority": "high"
        },
        {
            "task": "Update resume with recent experience",
            "gen_task_id": "a102",
            "time_estimate": "01:30",
            "dependencies": [],
            "priority": "high"
        },
        {
            "task": "Practice common interview questions",
            "gen_task_id": "a103",
            "time_estimate": "00:45",
            "dependencies": ["a101", "a102"],
            "priority": "high"
        },
        {
            "task": "Confirm interview time and location",
            "gen_task_id": "b201",
            "time_estimate": "00:10",
            "dependencies": [],
            "priority": "medium"
        },
        {
            "task": "Shop for professional interview attire",
            "gen_task_id": "c301",
            "time_estimate": "01:00",
            "dependencies": [],
            "priority": "low"
        }
    ]
}

GROCERY_TODO_RESPONSE = {
    "analysis": "Grocery and cooking tasks broken down into planning and execution phases.",
    "tasks": [
        {
            "task": "Create grocery shopping list",
            "gen_task_id": "a101",
            "time_estimate": "00:15", 
            "dependencies": [],
            "priority": "medium"
        },
        {
            "task": "Go to grocery store and shop",
            "gen_task_id": "a102",
            "time_estimate": "01:00",
            "dependencies": ["a101"],
            "priority": "medium"
        },
        {
            "task": "Prepare and cook dinner",
            "gen_task_id": "a103", 
            "time_estimate": "00:45",
            "dependencies": ["a102"],
            "priority": "high"
        }
    ]
}

# Mock HTTP responses for requests.post calls
def mock_claude_success_response(response_data):
    """Create a mock successful Claude API response"""
    class MockResponse:
        def __init__(self, json_data):
            self.json_data = json_data
            
        def raise_for_status(self):
            pass
            
        def json(self):
            return {
                'content': [{'text': json.dumps(response_data)}]
            }
    
    return MockResponse(response_data)

def mock_claude_error_response(status_code=500, error_message="API Error"):
    """Create a mock error Claude API response"""
    class MockResponse:
        def __init__(self, status_code, error_message):
            self.status_code = status_code
            self.error_message = error_message
            
        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception(f"HTTP {self.status_code}: {self.error_message}")
            
        def json(self):
            return {"error": self.error_message}
    
    return MockResponse(status_code, error_message)

def mock_claude_invalid_json_response():
    """Create a mock Claude API response with invalid JSON"""
    class MockResponse:
        def raise_for_status(self):
            pass
            
        def json(self):
            return {
                'content': [{'text': 'This is not valid JSON response from Claude'}]
            }
    
    return MockResponse()

# Test todo inputs
TEST_TODOS = {
    'simple': "Call dentist",
    'complex': """
        I need to prepare for my job interview next week. I should research the company,
        update my resume, practice common interview questions, and buy a new shirt.
        Also need to confirm the interview time and location.
    """,
    'grocery': "Buy groceries and cook dinner tonight",
    'empty': "",
    'long': "Task " * 500,  # Very long input for stress testing
    'morning_routine': """
        wake up, tell my gramma to take her meds, call my mom, cook and eat breakfast, 
        dont forget to brush my teeth, and get ready for work. get to the bus stop by 8:30am, 
        and then get to work by 9:00am. I need to finish the report by 10:00am, and then 
        have a meeting with the team at 11:00am.
    """
}

# Expected response mappings
RESPONSE_MAPPING = {
    'simple': SIMPLE_TODO_RESPONSE,
    'complex': COMPLEX_TODO_RESPONSE, 
    'grocery': GROCERY_TODO_RESPONSE,
}