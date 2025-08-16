I tested the following:

1. Personal Assistance Landing: http://127.0.0.1:8000/personal-assistance/
2. Executive Function:  http://127.0.0.1:8000/personal-assistance/executive-function/
3. ToDo Timeline Input: http://127.0.0.1:8000/personal-assistance/executive-function/todo-timeline/
4. The old home page is still at http://127.0.0.1:8000/ 

1 and 2 are doing okay.

3 looks okay. UI is okay. Functionality is not okay. this will be fixed later, when we get the AI integration working. 

4 is not working and we dont need to keep it. The AI integration should be used with the user input from http://127.0.0.1:8000/personal-assistance/executive-function/todo-timeline/ via the "groom my list" button. Also, we dont need to place a name on the todo list for now. so that user input should not be there. or at least show a message that its just for mock and not functional. 

all the views except 1 should have "back" buttons as part of the ui and should navigate to the previous screen. 