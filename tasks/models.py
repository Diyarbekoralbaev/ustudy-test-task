from django.db import models
from users.models import UserModel


class PriorityChoiceField(models.TextChoices):
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'

class TaskModel(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=20, choices=PriorityChoiceField.choices, default=PriorityChoiceField.LOW)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    deadline = models.DateTimeField()
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='tasks')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
