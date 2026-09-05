import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reckon.settings")

app = Celery("reckon")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "raise-due-reviews-every-morning": {
        "task": "decisions.tasks.raise_due_reviews",
        "schedule": 60 * 30,
    },
}
