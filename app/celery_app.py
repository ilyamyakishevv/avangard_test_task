from celery import Celery

from config import CHECK_INTERVAL

app = Celery("tasks", broker="redis://redis:6379/0", backend="redis://redis:6379/0", include=["tasks"])

app.conf.beat_schedule = {
    "check-treshold-prices-every-5-minutes": {
        "task": "tasks.check_treshold_prices_task",
        "schedule": float(CHECK_INTERVAL),
    },
}

app.conf.timezone = 'UTC'