from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from decisions.constants import (
    CATEGORY_CHOICES,
    CATEGORY_OTHER,
    CHALLENGE_PENDING,
    CHALLENGE_STATUS_CHOICES,
    NOTIFICATION_KIND_CHOICES,
    OUTCOME_CHOICES,
    STATUS_CHOICES,
    STATUS_DRAFT,
)
from reckon.models import BaseModel

CONFIDENCE_VALIDATORS = [MinValueValidator(0), MaxValueValidator(100)]


class Decision(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="decisions")
    title = models.CharField(max_length=200)
    context = models.TextField(help_text="Why this decision is being made, in the user's own words.")
    options_considered = models.JSONField(default=list, blank=True)
    chosen_option = models.CharField(max_length=300)
    expected_outcome = models.TextField(help_text="What the user expects to happen if they go ahead.")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_OTHER)

    # Confidence before the AI argued back, and after. The gap between them is
    # the most interesting number in the app.
    initial_confidence = models.PositiveSmallIntegerField(validators=CONFIDENCE_VALIDATORS)
    final_confidence = models.PositiveSmallIntegerField(validators=CONFIDENCE_VALIDATORS, null=True, blank=True)

    review_date = models.DateField(db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT, db_index=True)
    locked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "decisions_decision"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "status", "review_date"])]

    def __str__(self):
        return self.title

    @property
    def scored_confidence(self):
        """The number the user actually committed to."""
        return self.final_confidence if self.final_confidence is not None else self.initial_confidence


class Challenge(BaseModel):
    decision = models.OneToOneField(Decision, on_delete=models.CASCADE, related_name="challenge")
    status = models.CharField(max_length=20, choices=CHALLENGE_STATUS_CHOICES, default=CHALLENGE_PENDING)
    counterarguments = models.JSONField(default=list, blank=True)
    blind_spots = models.JSONField(default=list, blank=True)
    failure_conditions = models.JSONField(default=list, blank=True)
    sharpest_question = models.TextField(blank=True)
    provider = models.CharField(max_length=40, blank=True)

    class Meta:
        db_table = "decisions_challenge"

    def __str__(self):
        return f"Challenge for {self.decision_id}"


class Review(BaseModel):
    decision = models.OneToOneField(Decision, on_delete=models.CASCADE, related_name="review")
    outcome = models.CharField(max_length=10, choices=OUTCOME_CHOICES)
    what_happened = models.TextField()
    lesson = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "decisions_review"

    def __str__(self):
        return f"{self.outcome} - {self.decision_id}"


class Notification(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    decision = models.ForeignKey(Decision, on_delete=models.CASCADE, related_name="notifications", null=True)
    kind = models.CharField(max_length=30, choices=NOTIFICATION_KIND_CHOICES)
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "decisions_notification"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "decision", "kind"],
                name="uniq_notification_per_decision_kind",
            )
        ]

    def __str__(self):
        return self.title
