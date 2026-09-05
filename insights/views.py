from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from insights.utils import build_track_record


class TrackRecordView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(build_track_record(request.user))
