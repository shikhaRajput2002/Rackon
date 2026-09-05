from django.conf import settings
from django.db import models

from reckon.models import BaseModel


class Note(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notes")
    title = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    is_pinned = models.BooleanField(default=False)

    class Meta:
        db_table = "notes_note"
        ordering = ["-is_pinned", "-modified_at"]

    def __str__(self):
        return self.title or self.body[:40]
