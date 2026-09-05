from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from decisions.constants import STATUS_LOCKED
from decisions.models import Decision, Notification
from home.constants import RECENT_NOTES_ON_HOME
from home.utils import quote_for_date
from insights.utils import build_track_record
from notes.models import Note
from notes.serializers import NoteSerializer
from profiles.models import Profile
from profiles.serializers import ProfileSerializer


class HomeView(APIView):
    """Everything the home screen needs, in one request instead of five."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        today = timezone.localdate()

        notes = Note.objects.filter(user=request.user, is_deleted=False)[:RECENT_NOTES_ON_HOME]
        due_count = Decision.objects.filter(
            user=request.user,
            is_deleted=False,
            status=STATUS_LOCKED,
            review_date__lte=today,
        ).count()
        unread_count = Notification.objects.filter(user=request.user, is_deleted=False, read_at__isnull=True).count()

        return Response(
            {
                "user": {"name": request.user.name, "email": request.user.email},
                "quote": quote_for_date(today),
                "profile": ProfileSerializer(profile).data,
                "track_record": build_track_record(request.user),
                "notes": NoteSerializer(notes, many=True).data,
                "reviews_due": due_count,
                "unread_notifications": unread_count,
            }
        )
