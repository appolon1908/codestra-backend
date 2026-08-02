import os

from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CORE.settings')

app = Celery('CORE')


app.config_from_object('django.conf:settings', namespace='CELERY')


app.conf.broker_connection_retry_on_startup = True
# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
    

app.conf.beat_schedule = {
    'publish_scheduled_blogs': {
        'task': 'blog_app.tasks.publish_scheduled_blogs',
        'schedule': crontab(minute=0, hour='*'),
    }
}