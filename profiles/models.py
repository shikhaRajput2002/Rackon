from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from reckon.models import BaseModel
from profiles.constants import (
    DEFAULT_CURRENCY,
    EMPLOYMENT_CHOICES,
    EMPLOYMENT_SALARIED,
    REQUIRED_FOR_ADVICE,
    RISK_CHOICES,
    RISK_MEDIUM,
)

MONEY = {"max_digits": 14, "decimal_places": 2, "validators": [MinValueValidator(0)]}


class Profile(BaseModel):
    """
    What the advisor needs to know before it can say anything useful about
    whether someone can afford a thing.
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")

    age = models.PositiveSmallIntegerField(null=True, blank=True)
    city = models.CharField(max_length=80, blank=True)
    dependents = models.PositiveSmallIntegerField(default=0)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_CHOICES, default=EMPLOYMENT_SALARIED)

    currency = models.CharField(max_length=3, default=DEFAULT_CURRENCY)
    monthly_income = models.DecimalField(null=True, blank=True, **MONEY)
    monthly_expenses = models.DecimalField(null=True, blank=True, **MONEY)
    current_savings = models.DecimalField(null=True, blank=True, **MONEY)
    existing_emi = models.DecimalField(default=0, **MONEY)

    risk_appetite = models.CharField(max_length=10, choices=RISK_CHOICES, default=RISK_MEDIUM)
    goals = models.TextField(blank=True, help_text="What they are saving or working toward.")

    class Meta:
        db_table = "profiles_profile"

    def __str__(self):
        return f"Profile for {self.user_id}"

    @property
    def is_complete(self):
        return all(getattr(self, field) is not None for field in REQUIRED_FOR_ADVICE)
