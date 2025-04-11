import os

from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "apirewards.settings")

app = Celery("apirewards")
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
