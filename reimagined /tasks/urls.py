from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('process/', views.process_todo, name='process_todo'),
    path('results/<int:task_list_id>/', views.results, name='results'),
]