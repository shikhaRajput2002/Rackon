from django.conf import settings
from django.db import models

from advisor.constants import ROLE_CHOICES, TOPIC_CHOICES, TOPIC_GENERAL
from reckon.models import BaseModel


class AdvisorMessage(BaseModel):
    """
    One turn of the conversation. Assistant turns also carry the structured
    payload the UI renders — the arithmetic, the things to weigh, and a
    ready-to-log decision.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="advisor_messages")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    topic = models.CharField(max_length=20, choices=TOPIC_CHOICES, default=TOPIC_GENERAL)
    numbers = models.JSONField(default=list, blank=True)
    considerations = models.JSONField(default=list, blank=True)
    watch_outs = models.JSONField(default=list, blank=True)
    suggested_decision = models.JSONField(default=dict, blank=True)
    provider = models.CharField(max_length=40, blank=True)

    class Meta:
        db_table = "advisor_message"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.content[:40]}"
