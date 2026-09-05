from rest_framework import serializers

from profiles.models import Profile
from profiles.utils import build_profile_context


class ProfileSerializer(serializers.ModelSerializer):
    is_complete = serializers.BooleanField(read_only=True)
    derived = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "uuid",
            "age",
            "city",
            "dependents",
            "employment_type",
            "currency",
            "monthly_income",
            "monthly_expenses",
            "current_savings",
            "existing_emi",
            "risk_appetite",
            "goals",
            "is_complete",
            "derived",
            "modified_at",
        ]

    def get_derived(self, obj):
        """Disposable income and runway, computed once per response."""
        if not hasattr(obj, "_cached_derived"):
            context = build_profile_context(obj)
            obj._cached_derived = {
                "monthly_disposable": context["monthly_disposable"],
                "emergency_fund_months": context["emergency_fund_months"],
            }
        return obj._cached_derived


class ProfileWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "age",
            "city",
            "dependents",
            "employment_type",
            "currency",
            "monthly_income",
            "monthly_expenses",
            "current_savings",
            "existing_emi",
            "risk_appetite",
            "goals",
        ]
