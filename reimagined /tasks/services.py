import json
from huggingface_hub import InferenceClient
from django.conf import settings
from .models import TaskList, Task


class TaskGroomer:
    def __init__(self):
        api_key = getattr(settings, 'HUGGINGFACE_API_KEY', None)
        if not api_key:
            raise ValueError(
                "HUGGINGFACE_API_KEY not configured. "
                "Please add your Hugging Face API key to the .env file:\n"
                "1. Open the .env file in the project root\n"
                "2. Uncomment and set: HUGGINGFACE_API_KEY=your_actual_api_key_here\n"
                "3. Get your API key from: https://huggingface.co/settings/tokens"
            )
        self.client = InferenceClient("mistralai/Mixtral-8x7B-Instruct-v0.1", token=api_key)

    def groom_tasks(self, todo_text: str):
        prompt = f"""
        Analyze the following todo list and convert it into structured tasks with time estimates and dependencies.
        
        Todo list:
        {todo_text}
        
        Return ONLY a valid JSON array with this exact structure:
        [
            {{
                "title": "Task name",
                "description": "Detailed description",
                "estimated_duration": 30,
                "can_run_parallel": false,
                "dependencies": []
            }}
        ]
        
        Rules:
        - estimated_duration is in minutes
        - can_run_parallel indicates if task can be done alongside others
        - dependencies is array of task titles this task depends on
        - Only return the JSON array, no other text
        """
        
        try:
            response = self.client.text_generation(
                prompt, 
                max_new_tokens=800, 
                temperature=0.2,
                return_full_text=False
            )
            
            # Clean the response to ensure it's valid JSON
            cleaned_response = response.strip()
            if not cleaned_response.startswith('['):
                # Find the first [ in the response
                start_idx = cleaned_response.find('[')
                if start_idx != -1:
                    cleaned_response = cleaned_response[start_idx:]
                else:
                    raise ValueError("No valid JSON array found in response")
            
            # Find the last ] in the response
            end_idx = cleaned_response.rfind(']')
            if end_idx != -1:
                cleaned_response = cleaned_response[:end_idx + 1]
            
            return json.loads(cleaned_response)
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse AI response as JSON: {e}")
        except Exception as e:
            raise Exception(f"AI service error: {e}")

    def create_task_list_from_groomed_tasks(self, name: str, raw_input: str, groomed_tasks: list):
        task_list = TaskList.objects.create(
            name=name,
            raw_input=raw_input
        )
        
        # Create tasks first
        created_tasks = {}
        for task_data in groomed_tasks:
            task = Task.objects.create(
                title=task_data["title"],
                description=task_data["description"],
                estimated_duration=task_data["estimated_duration"],
                can_run_parallel=task_data.get("can_run_parallel", False),
                task_list=task_list
            )
            created_tasks[task_data["title"]] = task
        
        # Set up dependencies after all tasks are created
        for task_data in groomed_tasks:
            if task_data.get("dependencies"):
                task = created_tasks[task_data["title"]]
                for dep_title in task_data["dependencies"]:
                    if dep_title in created_tasks:
                        task.dependencies.add(created_tasks[dep_title])
        
        return task_list

    def process_todo(self, name: str, todo_text: str):
        groomed_tasks = self.groom_tasks(todo_text)
        return self.create_task_list_from_groomed_tasks(name, todo_text, groomed_tasks)