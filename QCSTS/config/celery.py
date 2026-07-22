import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

app = Celery("cqsts")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "check-overdue-test-points": {
        "task": "apps.schedule.tasks.mark_overdue_test_points",
        "schedule": crontab(hour=6, minute=0),
    },
}
