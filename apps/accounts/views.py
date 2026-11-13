from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema

from .serializers import (
    LoginSerializer,
    UserProfileSerializer,
    LogoutSerializer,
    EmployeeCreateSerializer,
    EmployeeListSerializer,
    EmployeeUpdateSerializer,
)

from django.shortcuts import get_object_or_404
from rest_framework import generics
from .models import User
from .permissions import IsAdminRole


class LoginView(TokenObtainPairView):

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer


class RefreshTokenView(TokenRefreshView):

    permission_classes = [AllowAny]


class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=LogoutSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                },
            }
        },
        description="Logout by blacklisting the refresh token.",
    )
    def post(self, request):

        serializer = LogoutSerializer(data=request.data, context={"request": request})

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"success": True, "message": "Successfully logged out."},
            status=status.HTTP_200_OK,
        )


class ProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = UserProfileSerializer(request.user)

        return Response(
            {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
        )


class EmployeeListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        return User.objects.filter(role=User.Role.EMPLOYEE).order_by("-date_joined")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return EmployeeCreateSerializer

        return EmployeeListSerializer


class EmployeeDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        return User.objects.filter(role=User.Role.EMPLOYEE)

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return EmployeeUpdateSerializer

        return EmployeeListSerializer
