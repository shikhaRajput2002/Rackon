from django.contrib import admin

from decisions.models import Challenge, Decision, Notification, Review


@admin.register(Decision)
class DecisionAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "category", "status", "initial_confidence", "final_confidence", "review_date"]
    list_filter = ["status", "category"]
    search_fields = ["title"]


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ["decision", "status", "provider", "created_at"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["decision", "outcome", "reviewed_at"]
    list_filter = ["outcome"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "kind", "read_at", "created_at"]
