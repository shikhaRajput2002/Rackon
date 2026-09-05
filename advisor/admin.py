from django.contrib import admin

from advisor.models import AdvisorMessage


@admin.register(AdvisorMessage)
class AdvisorMessageAdmin(admin.ModelAdmin):
    list_display = ["user", "role", "topic", "provider", "created_at"]
    list_filter = ["role", "topic"]
