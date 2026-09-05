from django.contrib import admin

from profiles.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "employment_type", "monthly_income", "current_savings", "modified_at"]
    list_filter = ["employment_type", "risk_appetite"]
