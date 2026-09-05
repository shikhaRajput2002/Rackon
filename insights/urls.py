from django.urls import path

from insights.views import TrackRecordView

urlpatterns = [
    path("track-record/", TrackRecordView.as_view(), name="insights_track_record"),
]
