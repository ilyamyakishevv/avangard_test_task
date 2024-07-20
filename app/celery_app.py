from celery import Celery

app = Celery('tasks', broker='redis://redis:6379/0', backend='redis://redis:6379/0', include=["tasks"])

app.conf.beat_schedule = {
    'check-treshold-prices-every-5-minutes': {
        'task': 'tasks.check_treshold_prices_task',
        'schedule': 300.0,
    },
}

app.conf.timezone = 'UTC'