from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from datetime import datetime, timedelta
from users.models import UserModel
from .models import TaskModel
from django.utils import timezone


class TaskTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserModel.objects.create_user(username='testuser', password='testpassword123')
        self.client.force_authenticate(user=self.user)
        self.task_list_url = reverse('task-list')
        self.task_detail_url = lambda pk: reverse('task-detail', args=[pk])

        # Create a task
        self.task_data = {
            'title': 'Test Task',
            'description': 'Test description',
            'status': 'new',
            'deadline': (timezone.now() + timedelta(days=1)).isoformat()
        }
        self.task = TaskModel.objects.create(user=self.user, **self.task_data)

    def test_create_task(self):
        data = {
            'title': 'New Task',
            'description': 'New task description',
            'status': 'new',
            'deadline': (datetime.now() + timedelta(days=2)).isoformat()
        }
        response = self.client.post(self.task_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TaskModel.objects.count(), 2)  # 1 from setUp + 1 new task
        self.assertEqual(TaskModel.objects.get(title='New Task').title, 'New Task')

    def test_list_tasks(self):
        response = self.client.get(self.task_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only the task created in setUp
        self.assertEqual(response.data[0]['title'], 'Test Task')

    def test_get_task(self):
        response = self.client.get(self.task_detail_url(self.task.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Task')

    def test_update_task(self):
        data = {
            'title': 'Updated Task',
            'description': 'Updated description',
            'status': 'in_progress',
            'deadline': (datetime.now() + timedelta(days=3)).isoformat()
        }
        response = self.client.put(self.task_detail_url(self.task.pk), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated Task')

    def test_partial_update_task(self):
        data = {
            'status': 'completed'
        }
        response = self.client.patch(self.task_detail_url(self.task.pk), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'completed')

    def test_delete_task(self):
        response = self.client.delete(self.task_detail_url(self.task.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TaskModel.objects.count(), 0)

