from django.urls import path

from decisions.views import DecisionViewSet, NotificationViewSet

urlpatterns = [
    path(
        "notifications/",
        NotificationViewSet.as_view({"get": "list"}),
        name="notification_list",
    ),
    path(
        "notifications/<uuid:notification_uuid>/read/",
        NotificationViewSet.as_view({"patch": "mark_read"}),
        name="notification_mark_read",
    ),
    path("", DecisionViewSet.as_view({"get": "list", "post": "create"}), name="decision_list"),
    path(
        "<uuid:decision_uuid>/",
        DecisionViewSet.as_view({"get": "retrieve", "patch": "update", "delete": "destroy"}),
        name="decision_detail",
    ),
    path(
        "<uuid:decision_uuid>/challenge/",
        DecisionViewSet.as_view({"post": "challenge"}),
        name="decision_challenge",
    ),
    path(
        "<uuid:decision_uuid>/confidence/",
        DecisionViewSet.as_view({"patch": "revise_confidence"}),
        name="decision_confidence",
    ),
    path("<uuid:decision_uuid>/lock/", DecisionViewSet.as_view({"post": "lock"}), name="decision_lock"),
    path("<uuid:decision_uuid>/review/", DecisionViewSet.as_view({"post": "review"}), name="decision_review"),
]
