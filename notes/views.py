from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from notes.errors import NOTE_NOT_FOUND
from notes.models import Note
from notes.serializers import NoteSerializer, NoteWriteSerializer


class NoteViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def get_note(self, request, note_uuid):
        return Note.objects.filter(uuid=note_uuid, user=request.user, is_deleted=False).first()

    def list(self, request):
        notes = Note.objects.filter(user=request.user, is_deleted=False)
        return Response(NoteSerializer(notes, many=True).data)

    def create(self, request):
        serializer = NoteWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        note = Note.objects.create(user=request.user, **serializer.validated_data)
        return Response(NoteSerializer(note).data, status=201)

    def update(self, request, note_uuid):
        note = self.get_note(request, note_uuid)
        if not note:
            return NOTE_NOT_FOUND.response()

        serializer = NoteWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        for field, value in serializer.validated_data.items():
            setattr(note, field, value)
        note.save()
        return Response(NoteSerializer(note).data)

    def destroy(self, request, note_uuid):
        note = self.get_note(request, note_uuid)
        if not note:
            return NOTE_NOT_FOUND.response()

        note.is_deleted = True
        note.save(update_fields=["is_deleted", "modified_at"])
        return Response(status=204)
