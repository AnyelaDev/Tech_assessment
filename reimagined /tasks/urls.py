from django.urls import path
from . import views

urlpatterns = [
    # Original home and process routes
    path('', views.home, name='home'),
    path('process/', views.process_todo, name='process_todo'),
    path('results/<int:task_list_id>/', views.results, name='results'),
    
    # New navigation routes
    path('personal-assistance/', views.personal_assistance, name='personal_assistance'),
    path('personal-assistance/executive-function/', views.executive_function, name='executive_function'),
    path('personal-assistance/executive-function/todo-timeline/', views.todo_timeline_input, name='todo_timeline_input'),
    path('personal-assistance/executive-function/todo-timeline/process/', views.process_todo_timeline, name='process_todo_timeline'),
    path('personal-assistance/executive-function/todo-timeline/dependencies/<int:task_list_id>/', views.todo_dependencies, name='todo_dependencies'),
    path('personal-assistance/executive-function/todo-timeline/execute/<int:task_list_id>/', views.timeline_execution, name='timeline_execution'),
]