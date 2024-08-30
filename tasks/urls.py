from django.urls import path
from .views import TaskListView, TaskDetailView, AdminTaskListView

urlpatterns = [
    path('my/', TaskListView.as_view(), name='task-list'),
    path('my/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('all/', AdminTaskListView.as_view(), name='admin-task-list'),
]
