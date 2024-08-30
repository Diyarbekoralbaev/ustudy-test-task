import logging
from datetime import datetime, timedelta

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import TaskModel
from .serializers import TaskSerializer

logger = logging.getLogger(__name__)


class TaskListView(APIView):
    @swagger_auto_schema(
        tags=['Tasks'],
        operation_id='List tasks',
        operation_description='List all tasks',
        manual_parameters=[
            openapi.Parameter(
                'status', openapi.IN_QUERY,
                description="Filter tasks by status (new, in progress, completed)",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'year', openapi.IN_QUERY,
                description="Filter tasks by year",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'month', openapi.IN_QUERY,
                description="Filter tasks by month",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'day', openapi.IN_QUERY,
                description="Filter tasks by day",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: openapi.Response('List of tasks', TaskSerializer(many=True)),
            401: openapi.Response('Unauthorized', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING,
                                             description='Authentication credentials were not provided.')
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

            status_filter = request.query_params.get('status')
            year = request.query_params.get('year')
            month = request.query_params.get('month')
            day = request.query_params.get('day')

            # Validate and apply status filter
            if status_filter:
                if status_filter not in ['new', 'in_progress', 'completed']:
                    return Response({'detail': 'Invalid status filter'}, status=status.HTTP_400_BAD_REQUEST)
                tasks = tasks.filter(status=status_filter)

            if year:
                try:
                    start_date = datetime(year=int(year), month=1, day=1)
                    end_date = datetime(year=int(year) + 1, month=1, day=1)
                    tasks = tasks.filter(deadline__range=[start_date, end_date])
                except ValueError:
                    return Response({'detail': 'Invalid year format. Year must be an integer.'},
                                    status=status.HTTP_400_BAD_REQUEST)

            if month:
                try:
                    if not year:
                        return Response({'detail': 'Year must be provided with month.'},
                                        status=status.HTTP_400_BAD_REQUEST)
                    start_date = datetime(year=int(year), month=int(month), day=1)
                    # Calculate the last day of the month
                    next_month = start_date.replace(day=28) + timedelta(days=4)
                    end_date = next_month - timedelta(days=next_month.day)
                    tasks = tasks.filter(deadline__range=[start_date, end_date])
                except ValueError:
                    return Response({'detail': 'Invalid month format. Month must be an integer between 1 and 12.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                except TypeError:
                    return Response({'detail': 'Year and month must be integers.'}, status=status.HTTP_400_BAD_REQUEST)

            if day:
                try:
                    if not year or not month:
                        return Response({'detail': 'Year and month must be provided with day.'},
                                        status=status.HTTP_400_BAD_REQUEST)
                    start_date = datetime(year=int(year), month=int(month), day=int(day))
                    end_date = start_date + timedelta(days=1)
                    tasks = tasks.filter(deadline__range=[start_date, end_date])
                except ValueError:
                    return Response({'detail': 'Invalid day format. Day must be an integer.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                except TypeError:
                    return Response({'detail': 'Year, month, and day must be integers.'},
                                    status=status.HTTP_400_BAD_REQUEST)

            if not tasks.exists():
                return Response({'detail': 'No tasks found'}, status=status.HTTP_404_NOT_FOUND)

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
            logger.info(f'Task created: title={serializer.data["title"]} by user={request.user.username}')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f'Error while creating task: {serializer.errors}')
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
            logger.info(f'Task details retrieved: title={serializer.data["title"]} by user={request.user.username}')
            return Response(serializer.data)
        except TaskModel.DoesNotExist:
            logger.error(f'Task does not exist: pk={pk}')
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
            logger.info(f'Task details retrieved for update: title={task.title} by user={request.user.username}')
        except TaskModel.DoesNotExist:
            logger.error(f'Task does not exist: pk={pk}')
            return Response({'detail': 'Task does not exist'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(task, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            logger.info(f'Task updated: title={serializer.data["title"]} by user={request.user.username}')
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
            logger.info(
                f'Task details retrieved for partial update: title={task.title} by user={request.user.username}')
        except TaskModel.DoesNotExist:
            return Response({'detail': 'Task does not exist'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(task, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f'Task updated: title={serializer.data["title"]} by user={request.user.username}')
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
            logger.info(f'Task details retrieved for deletion: title={task.title} by user={request.user.username}')
        except TaskModel.DoesNotExist:
            logger.error(f'Task does not exist: pk={pk}')
            return Response({'detail': 'Task does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error('Internal server error', exc_info=e)
            return Response({'detail': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminTaskListView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure only super admins can access this view

    @swagger_auto_schema(
        tags=['Tasks'],
        operation_id='List all tasks (admin)',
        operation_description='List all tasks for super admin',
        manual_parameters=[
            openapi.Parameter(
                'status', openapi.IN_QUERY,
                description="Filter tasks by status (new, in progress, completed)",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'year', openapi.IN_QUERY,
                description="Filter tasks by year",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'month', openapi.IN_QUERY,
                description="Filter tasks by month",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'day', openapi.IN_QUERY,
                description="Filter tasks by day",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: openapi.Response('List of all tasks', TaskSerializer(many=True)),
            401: openapi.Response('Unauthorized', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING,
                                             description='Authentication credentials were not provided.')
                }
            )),
            403: openapi.Response('Forbidden', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='You do not have permission to perform this action.')
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
            tasks = TaskModel.objects.all()  # Get all tasks regardless of user

            status_filter = request.query_params.get('status')
            year = request.query_params.get('year')
            month = request.query_params.get('month')
            day = request.query_params.get('day')

            if status_filter:
                if status_filter not in ['new', 'in_progress', 'completed']:
                    return Response({'detail': 'Invalid status filter'}, status=status.HTTP_400_BAD_REQUEST)
                tasks = tasks.filter(status=status_filter)

            if year:
                try:
                    start_date = datetime(year=int(year), month=1, day=1)
                    end_date = datetime(year=int(year) + 1, month=1, day=1)
                    tasks = tasks.filter(deadline__range=[start_date, end_date])
                except ValueError:
                    return Response({'detail': 'Invalid year format. Year must be an integer.'},
                                    status=status.HTTP_400_BAD_REQUEST)

            if month:
                try:
                    if not year:
                        return Response({'detail': 'Year must be provided with month.'},
                                        status=status.HTTP_400_BAD_REQUEST)
                    start_date = datetime(year=int(year), month=int(month), day=1)
                    next_month = start_date.replace(day=28) + timedelta(days=4)
                    end_date = next_month - timedelta(days=next_month.day)
                    tasks = tasks.filter(deadline__range=[start_date, end_date])
                except ValueError:
                    return Response({'detail': 'Invalid month format. Month must be an integer between 1 and 12.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                except TypeError:
                    return Response({'detail': 'Year and month must be integers.'}, status=status.HTTP_400_BAD_REQUEST)

            if day:
                try:
                    if not year or not month:
                        return Response({'detail': 'Year and month must be provided with day.'},
                                        status=status.HTTP_400_BAD_REQUEST)
                    start_date = datetime(year=int(year), month=int(month), day=int(day))
                    end_date = start_date + timedelta(days=1)
                    tasks = tasks.filter(deadline__range=[start_date, end_date])
                except ValueError:
                    return Response({'detail': 'Invalid day format. Day must be an integer.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                except TypeError:
                    return Response({'detail': 'Year, month, and day must be integers.'},
                                    status=status.HTTP_400_BAD_REQUEST)

            if not tasks.exists():
                return Response({'detail': 'No tasks found'}, status=status.HTTP_404_NOT_FOUND)

            serializer = TaskSerializer(tasks, many=True)
            return Response(serializer.data)
        except Exception:
            return Response({'detail': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)