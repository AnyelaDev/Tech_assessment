import json
import requests
from django.conf import settings
from .models import TaskList, Task


class ClaudeTaskGroomer:
    def __init__(self):
        api_key = getattr(settings, 'CLAUDE_API_KEY', None)
        
        if not api_key:
            raise ValueError(
                "CLAUDE_API_KEY not configured. "
                "Please add your Claude API key to the .env file:\n"
                "1. Open the .env file in the project root\n"
                "2. Add: CLAUDE_API_KEY=your_actual_api_key_here\n"
                "3. Get your API key from: https://console.anthropic.com/"
            )
        
        self.api_key = api_key
        self.api_url = 'https://api.anthropic.com/v1/messages'
        self.headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01'
        }

    def groom_tasks(self, todo_text: str, context: str = ""):
        """
        Uses Claude Sonnet to groom and enhance a todo text statement from a user.
        
        Args:
            todo_text (str): The original todo text to be groomed
            context (str): Additional context about the project or task
        
        Returns:
            dict: Contains success status, analysis, and tasks
        """
        # Check for cheap AI test mode
        if todo_text.strip() == "Make 25 sandwiches" and "dont know if I have enough food" in context.lower():
            return self._get_cheap_test_response()
            
        # Check for development/testing mode with common test phrases
        if any(phrase in todo_text.lower() for phrase in ["test", "mock", "debug"]):
            return self._get_mock_response_for_testing(todo_text)
        
        prompt = f"""
You are a personal assistant. Your client will give you a text expressing things they must get done. Your task is to understand what is overwhelming the user, breakdown big tasks in smaller tasks and add them to the list. Identify individual tasks and suggest realistic time intervals in which each task could be done. Reword each task and make them more actionable and specific, no fluff, no emojis.

Original todo: "{todo_text}"

Additional context: {context if context else "No additional context provided"}

Please provide:
1. A list of actionable tasks derived from the original todo in the form of a JSON array. each object in the array should have:
   - "task": the reworded task
   - "gen_task_id": a unique identifier for this task that you generate (use any format you want - letters, numbers, etc.). This is only for mapping dependencies within this response.
   - "time_estimate": a realistic time estimate for completion (in hh:mm format). time estimates should be realistic and not too short
   - "dependencies": an array of gen_task_id values that this task depends on (if any)
   - "priority": a priority level (low, medium, high)
2. A brief analysis of the original todo text, explaining the breakdown and reasoning behind the tasks. as concise as possible.

IMPORTANT: Make sure all gen_task_id values are unique within your response, as they will be used to map task dependencies.

Format your response as a JSON.
"""
        
        payload = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            groomed_content = result['content'][0]['text']
            
            # Parse the JSON response
            try:
                parsed_response = json.loads(groomed_content)
                return {
                    "success": True,
                    "analysis": parsed_response.get("analysis", ""),
                    "tasks": parsed_response.get("tasks", [])
                }
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from the response
                start_idx = groomed_content.find('{')
                end_idx = groomed_content.rfind('}')
                if start_idx != -1 and end_idx != -1:
                    json_str = groomed_content[start_idx:end_idx + 1]
                    parsed_response = json.loads(json_str)
                    return {
                        "success": True,
                        "analysis": parsed_response.get("analysis", ""),
                        "tasks": parsed_response.get("tasks", [])
                    }
                else:
                    raise ValueError("Could not extract valid JSON from Claude response")
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"API request failed: {str(e)}",
                "analysis": "",
                "tasks": []
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "analysis": "",
                "tasks": []
            }

    def parse_time_estimate(self, time_str: str) -> int:
        """Convert time estimate from 'hh:mm' format to minutes"""
        try:
            parts = time_str.split(':')
            if len(parts) != 2:
                raise ValueError("Invalid time format")
            hours = int(parts[0])
            minutes = int(parts[1])
            if hours < 0 or minutes < 0 or minutes >= 60:
                raise ValueError("Invalid time values")
            return hours * 60 + minutes
        except (ValueError, IndexError):
            # Default to 30 minutes if parsing fails
            return 30

    def generate_unique_db_task_id(self, used_ids: set) -> str:
        """Generate a unique 4-character hex task_id for database storage"""
        import secrets
        
        while True:
            new_id = secrets.token_hex(2)  # 2 bytes = 4 hex chars
            if new_id not in used_ids and not Task.objects.filter(task_id=new_id).exists():
                return new_id


    def create_task_list_from_groomed_tasks(self, name: str, raw_input: str, groomed_result: dict):
        task_list = TaskList.objects.create(
            name=name,
            raw_input=raw_input
        )
        
        if not groomed_result.get("success"):
            raise ValueError(f"Claude API error: {groomed_result.get('error', 'Unknown error')}")
        
        tasks_data = groomed_result.get("tasks", [])
        
        # Create tasks first
        used_task_ids = set()
        gen_id_to_task_mapping = {}  # Map AI's gen_task_id to our Task objects
        
        for task_data in tasks_data:
            duration = self.parse_time_estimate(task_data.get("time_estimate", "00:30"))
            gen_task_id = task_data.get("gen_task_id", "unknown")  # AI's reference ID
            
            # Generate a unique database task_id (independent of AI's gen_task_id)
            final_task_id = self.generate_unique_db_task_id(used_task_ids)
            used_task_ids.add(final_task_id)
            
            task = Task.objects.create(
                title=task_data.get("task", "Untitled Task"),
                description=task_data.get("task", "Untitled Task"),
                task_id=final_task_id,
                priority=task_data.get("priority", "medium"),
                estimated_duration=duration,
                task_list=task_list
            )
            
            # Map AI's gen_task_id to our created Task object
            gen_id_to_task_mapping[gen_task_id] = task
        
        # Set up dependencies using AI's gen_task_id system
        for task_data in tasks_data:
            gen_task_id = task_data.get("gen_task_id", "unknown")
            
            if gen_task_id in gen_id_to_task_mapping and task_data.get("dependencies"):
                task = gen_id_to_task_mapping[gen_task_id]
                for gen_dep_id in task_data["dependencies"]:
                    if gen_dep_id in gen_id_to_task_mapping:
                        dependency_task = gen_id_to_task_mapping[gen_dep_id]
                        task.dependencies.add(dependency_task)
        
        return task_list, groomed_result.get("analysis", "")

    def process_todo(self, name: str, todo_text: str, context: str = ""):
        groomed_result = self.groom_tasks(todo_text, context)
        task_list, analysis = self.create_task_list_from_groomed_tasks(name, todo_text, groomed_result)
        return task_list, analysis


# Keep the old class name for backward compatibility
TaskGroomer = ClaudeTaskGroomer