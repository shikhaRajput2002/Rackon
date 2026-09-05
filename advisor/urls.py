from django.urls import path

from advisor.views import AdvisorView

urlpatterns = [
    path("", AdvisorView.as_view(), name="advisor"),
]
