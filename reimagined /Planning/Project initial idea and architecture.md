## About the team
The developer is comfortable with **Python and Django** but not too experienced with front-end frameworks.

---

# MindTimer (Name is subject to change!)

**Project Overview**
MindTimer will help users convert a free-form to-do list into a structured schedule with estimated times, dependencies, and opportunities for parallel execution (e.g., laundry while cooking). Users can then follow the plan with automated timers and notifications.

**Core Value Proposition**
MindTimer simplifies personal task management by turning an unstructured list into an actionable plan, highlighting task order, time estimates, and parallelizable activities, while saving progress across sessions.
It will probably have other functionalities later. 
---

## Technology Stack

**Frontend**
- Minimalistic: basic HTML, CSS, and JavaScript.
- Use **Django templates** to render pages; for simplicity.
* Use small JavaScript snippets only for timers and interactive elements.

**Backend**

* **Python + Django** for the backend.
* All business logic — task planning, scheduling, LLM calls — implemented in Python.
* **SQLite** for local prototyping; migrate to **Postgres via Supabase** when needed.

**LLM Integration**

* Hugging Face API key + Python library for remote inference.
* One Python function receives the to-do text, queries the model, and returns structured JSON with tasks, durations, and dependencies.

Example: (To be tested)

```python
from huggingface_hub import InferenceClient

client = InferenceClient("mistralai/Mixtral-8x7B-Instruct-v0.1")

def groom_tasks(todo_text: str):
    prompt = f"Organize the following todo list into tasks with time estimates and dependencies.\n{todo_text}\nReturn JSON."
    response = client.text_generation(prompt, max_new_tokens=400, temperature=0.2)
    return response  # parse JSON from response
```

**Packaging & Deployment**

* **Web-first deployment** using Django.
* Users can access via browser on mobile or desktop.
* Optional: PWA or lightweight desktop wrappers (Tauri/Electron) later.

---

## Architecture

1. **User Input**: Plain-text to-do list submitted via a Django HTML form.
2. **LLM Processing**: Python function calls Hugging Face to normalize tasks, estimate times, and infer dependencies.
3. **Planner Algorithm**: Python module builds schedule with sequential and parallel blocks.
4. **Persistence Layer**: Start with SQLite; migrate to Supabase/Postgres as needed.
5. **Execution Layer**: Django-rendered page displays the plan; simple JavaScript timers manage task countdowns.

---