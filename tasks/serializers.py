from django.utils import timezone

from rest_framework import serializers
from .models import TaskModel


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskModel
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

    def validate_deadline(self, value):
        if value < timezone.now():
            raise serializers.ValidationError('Deadline must be in the future')
        if value.year > value.created_at:
            raise serializers.ValidationError('Deadline must be in the future')
        return value

    def create(self, validated_data):
        task = TaskModel.objects.create(user=self.context['request'].user, **validated_data)
        return task

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.status = validated_data.get('status', instance.status)
        instance.deadline = validated_data.get('deadline', instance.deadline)
        instance.save()
        return instance

