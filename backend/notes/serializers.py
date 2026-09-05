from rest_framework import serializers

from notes.models import Note


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ["uuid", "title", "body", "is_pinned", "created_at", "modified_at"]


class NoteWriteSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200, required=False, allow_blank=True)
    body = serializers.CharField()
    is_pinned = serializers.BooleanField(required=False)
