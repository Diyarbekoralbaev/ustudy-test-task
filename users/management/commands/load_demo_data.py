import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from users.models import UserModel
from tasks.models import TaskModel

fake = Faker()


class Command(BaseCommand):
    help = 'Create demo data for users and tasks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of users to create'
        )
        parser.add_argument(
            '--tasks',
            type=int,
            default=50,
            help='Number of tasks to create'
        )

    def handle(self, *args, **options):
        num_users = options['users']
        num_tasks = options['tasks']

        self.stdout.write(self.style.SUCCESS(f'Creating {num_users} users and {num_tasks} tasks...'))

        # Create users
        users = []
        user = UserModel.objects.create_user(
            username='admin',
            password='admin',
        )
        users.append(user)
        self.stdout.write(self.style.SUCCESS(f'Created user: {user.username}'))
        for _ in range(num_users):
            user = UserModel.objects.create_user(
                username=fake.user_name(),
                password=fake.password()
            )
            users.append(user)
            self.stdout.write(self.style.SUCCESS(f'Created user: {user.username}'))

        # Define statuses
        statuses = ['new', 'in_progress', 'completed']

        # Create tasks
        for _ in range(num_tasks):
            user = random.choice(users)
            status = random.choice(statuses)

            # Generate a deadline with varying year, month, day, and hour
            current_time = timezone.now()
            deadline_year = random.randint(current_time.year, current_time.year + 2)
            deadline_month = random.randint(1, 12)
            deadline_day = random.randint(1, 28)  # Avoid issues with days in different months
            deadline_hour = random.randint(0, 23)

            try:
                deadline = timezone.make_aware(
                    timezone.datetime(
                        year=deadline_year,
                        month=deadline_month,
                        day=deadline_day,
                        hour=deadline_hour,
                        minute=0,
                        second=0
                    )
                )
            except ValueError:
                # Handle the case where the day is invalid for the given month
                continue

            task = TaskModel.objects.create(
                title=fake.sentence(),
                description=fake.text(),
                status=status,
                deadline=deadline,
                user=user
            )
            self.stdout.write(
                self.style.SUCCESS(f'Created task: {task.title} with status: {status} for user: {user.username}'))

        self.stdout.write(self.style.SUCCESS('Demo data creation complete.'))