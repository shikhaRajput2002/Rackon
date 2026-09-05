from django.urls import path

from accounts.views import LoginView, MeView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth_register"),
    path("login/", LoginView.as_view(), name="auth_login"),
    path("me/", MeView.as_view(), name="auth_me"),
]
