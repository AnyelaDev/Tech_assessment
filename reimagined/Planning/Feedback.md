# Feedback

# Expected Behavior

  models functionality:
  - The UI should allow the user to enter the 2 text inputs needed by AI inference: todo_text, context. No need to name the list. 
  - Task: estimated duration and durations in general appear buggy in UI, especifically in the "Time left" in the Timeline screen.
  - Validation: ✅ Has basic validation in clean() method
  - Dependencies: they dont show correctly in UI. User should be able to check the dependencies.

  Questions about Expected Behavior

  1. Missing can_overlap field
  can_run_parallel is better. I will change the acceptance criteria in github, you can update it in the Issues.md
  2. Model validation scope
  - Required basic field validation
  - Avoid circular dependencies.
  - task_id should be given by our program, the inference could make a mistake. we must make sure they are all correct and the right format: 4 bytes Hex. 

  3. Field naming consistency
  - Keep estimated_duration 
  - update acceptance criteria in Issues.md

  4. Dependencies enhancement
  - In the UI the information that shows is "Dependencies: <tasks.Task.None>" for every task. This is not the expected behavior. It should be more descriptive via dependent tasks ID
  - Add additional dependency-related methods and validation:
   - avoid circular dependency
   - the method should be:
        - enter 0000, removes dependencies
        - enter any other valid 4 digit hex, adds a dependency. 
        - each task can have up to 4 dependencies.
        - Dependency means those tasks cant start until the present task is finished
  - Focus on making it more user-friendly via clear ui.

  5. Scope of "minimal"

  Since the issue is about "minimal models explicitly", should I:
  - Do not Remove existing fields not mentioned in criteria yet. We need them for debugging. actually show them in the UI.
  - Keep existing working fields and just ensure the criteria fields exist