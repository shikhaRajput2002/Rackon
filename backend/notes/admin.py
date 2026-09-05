from django.contrib import admin

from notes.models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ["__str__", "user", "is_pinned", "modified_at"]
    list_filter = ["is_pinned"]
