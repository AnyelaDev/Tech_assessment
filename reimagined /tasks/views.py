from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import TaskList, Task
from .services import TaskGroomer


def home(request):
    return render(request, 'tasks/home.html')


def process_todo(request):
    if request.method != 'POST':
        return redirect('home')
    
    task_list_name = request.POST.get('task_list_name', '').strip()
    todo_text = request.POST.get('todo_text', '').strip()
    
    if not task_list_name or not todo_text:
        return render(request, 'tasks/home.html', {
            'error': 'Both task list name and todo text are required.'
        })
    
    try:
        groomer = TaskGroomer()
        task_list = groomer.process_todo(task_list_name, todo_text)
        return redirect('results', task_list_id=task_list.id)
    except ValueError as e:
        return render(request, 'tasks/home.html', {
            'error': str(e),
            'task_list_name': task_list_name,
            'todo_text': todo_text
        })


def results(request, task_list_id):
    task_list = get_object_or_404(TaskList, id=task_list_id)
    tasks = task_list.tasks.all()
    
    return render(request, 'tasks/results.html', {
        'task_list': task_list,
        'tasks': tasks,
        'total_time': task_list.total_estimated_time()
    })
