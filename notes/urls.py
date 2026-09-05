from django.urls import path

from notes.views import NoteViewSet

urlpatterns = [
    path("", NoteViewSet.as_view({"get": "list", "post": "create"}), name="note_list"),
    path(
        "<uuid:note_uuid>/",
        NoteViewSet.as_view({"patch": "update", "delete": "destroy"}),
        name="note_detail",
    ),
]
