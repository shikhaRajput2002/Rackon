from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.errors import EMAIL_ALREADY_REGISTERED, INVALID_CREDENTIALS
from accounts.models import User
from accounts.serializers import LoginSerializer, RegisterSerializer, UserSerializer
from accounts.utils import build_auth_response


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        email = data["email"].lower()
        if User.objects.filter(email=email).exists():
            return EMAIL_ALREADY_REGISTERED.response(details={"email": email})

        user = User.objects.create_user(email=email, password=data["password"], name=data.get("name", ""))
        return Response(build_auth_response(user), status=201)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = User.objects.filter(email=data["email"].lower(), is_active=True).first()
        if not user or not user.check_password(data["password"]):
            return INVALID_CREDENTIALS.response()

        return Response(build_auth_response(user))


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
