from rest_framework_simplejwt.tokens import RefreshToken

from accounts.serializers import UserSerializer


def build_auth_response(user):
    """Every auth endpoint hands back the same shape."""
    refresh = RefreshToken.for_user(user)
    return {
        "user": UserSerializer(user).data,
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh),
    }
