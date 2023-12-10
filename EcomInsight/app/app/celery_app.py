import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
app = Celery('app')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_url = settings.CELERY_BROKER_URL
app.autodiscover_tasks()


@app.task()
def debug_task(self):
    print(f'Request: {self.request!r}')
    print(f'Hello from debug task.')
