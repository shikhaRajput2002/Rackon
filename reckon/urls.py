from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/home/", include("home.urls")),
    path("api/profile/", include("profiles.urls")),
    path("api/notes/", include("notes.urls")),
    path("api/advisor/", include("advisor.urls")),
    path("api/decisions/", include("decisions.urls")),
    path("api/insights/", include("insights.urls")),
]
