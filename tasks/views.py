from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import TaskModel
from .serializers import TaskSerializer


class TaskListView(APIView):
    @swagger_auto_schema(
        tags=['Tasks'],
        operation_id='List tasks',
        operation_description='List all tasks',
        responses={
            200: openapi.Response('List of tasks', TaskSerializer(many=True)),
            401: openapi.Response('Unauthorized', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Authentication credentials were not provided.')
                }
            )),
            404: openapi.Response('No tasks found', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='No tasks found')
                }
            )),
            500: openapi.Response('Internal server error', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Internal server error')
                }
            )),
        }
    )
    def get(self, request):
        try:
            tasks = TaskModel.objects.filter(user=request.user)
            serializer = TaskSerializer(tasks, many=True)
            return Response(serializer.data)
        except TaskModel.DoesNotExist:
            return Response({'detail': 'No tasks found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({'detail': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        tags=['Tasks'],
        operation_id='Create a task',
        operation_description='Create a task',
        request_body=TaskSerializer,
        responses={
            201: openapi.Response('Task created', TaskSerializer),
            400: openapi.Response('Validation error', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Validation error')
                }
            )),
            401: openapi.Response('Unauthorized', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING,
                                             description='Authentication credentials were not provided.')
                }
            )),
        }
    )
    def post(self, request):
        serializer = TaskSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailView(APIView):
    @swagger_auto_schema(
        tags=['Tasks'],
        operation_id='Get a task',
        operation_description='Get a task',
        responses={
            200: openapi.Response('Task details', TaskSerializer),
            401: openapi.Response('Unauthorized', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING,
                                             description='Authentication credentials were not provided.')
                }
            )),
            404: openapi.Response('Task does not exist', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Task does not exist')
                }
            )),
        }
    )
    def get(self, request, pk):
        try:
            task = TaskModel.objects.get(pk=pk, user=request.user)
            serializer = TaskSerializer(task)
            return Response(serializer.data)
        except TaskModel.DoesNotExist:
            return Response({'detail': 'Task does not exist'}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        tags=['Tasks'],
        operation_id='Update a task',
        operation_description='Update a task',
        request_body=TaskSerializer,
        responses={
            200: openapi.Response('Task updated', TaskSerializer),
            400: openapi.Response('Validation error', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Validation error')
                }
            )),
            401: openapi.Response('Unauthorized', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING,
                                             description='Authentication credentials were not provided.')
                }
            )),
            404: openapi.Response('Task does not exist', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Task does not exist')
                }
            )),
        }
    )
    def put(self, request, pk):
        try:
            task = TaskModel.objects.get(pk=pk, user=request.user)
        except TaskModel.DoesNotExist:
            return Response({'detail': 'Task does not exist'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(task, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=['Tasks'],
        operation_id='Partial update a task',
        operation_description='Partial update a task',
        request_body=TaskSerializer,
        responses={
            200: openapi.Response('Task updated', TaskSerializer),
            400: openapi.Response('Validation error', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Validation error')
                }
            )),
            401: openapi.Response('Unauthorized', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING,
                                             description='Authentication credentials were not provided.')
                }
            )),
            404: openapi.Response('Task does not exist', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Task does not exist')
                }
            )),
        }
    )
    def patch(self, request, pk):
        try:
            task = TaskModel.objects.get(pk=pk, user=request.user)
        except TaskModel.DoesNotExist:
            return Response({'detail': 'Task does not exist'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(task, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=['Tasks'],
        operation_id='Delete a task',
        operation_description='Delete a task',
        responses={
            204: openapi.Response('Task deleted', None),
            401: openapi.Response('Unauthorized', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING,
                                             description='Authentication credentials were not provided.')
                }
            )),
            404: openapi.Response('Task does not exist', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Task does not exist')
                }
            )),
            500: openapi.Response('Internal server error', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Internal server error')
                }
            )),
        }
    )
    def delete(self, request, pk):
        try:
            task = TaskModel.objects.get(pk=pk, user=request.user)
        except TaskModel.DoesNotExist:
            return Response({'detail': 'Task does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({'detail': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
