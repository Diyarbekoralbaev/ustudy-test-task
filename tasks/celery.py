from celery import Celery
from celery.schedules import crontab

app = Celery('ustudy_test_task')
