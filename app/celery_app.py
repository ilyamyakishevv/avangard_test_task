from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

app.conf.beat_schedule = {
    'check-treshold-prices-every-5-minutes': {
        'task': 'tasks.check_treshold_prices_task',
        'schedule': 30.0,
    },
}

app.conf.timezone = 'UTC'