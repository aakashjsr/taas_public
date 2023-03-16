from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_403_FORBIDDEN
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

from .models import User
from .serializers import UserSerializer
from .permissions import AppAdminPermission


class UserCreateView(CreateAPIView):
    permission_classes = (AppAdminPermission,)
    serializer_class = UserSerializer


class UserRUDView(RetrieveUpdateDestroyAPIView):
    permission_classes = (AppAdminPermission,)
    serializer_class = UserSerializer
    queryset = User.objects.all()


class LoginView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if email and password:
            user = User.objects.filter(email__iexact=email).first()
            if user and user.check_password(password):
                token, _ = Token.objects.get_or_create(user=user)
                response = UserSerializer(user).data
                response["token"] = token.key
                return Response(response)
            return Response(
                {"detail": "Invalid credentials"}, status=HTTP_403_FORBIDDEN
            )
        return Response(
            {"detail": "Please provide credentials"}, status=HTTP_403_FORBIDDEN
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response({})


class TaggableUserListView(APIView):
    def get(self, request, *args, **kwargs):
        data = [{"id": u.id, "display": u.get_full_name()} for u in User.objects.all()]
        return Response(data)
