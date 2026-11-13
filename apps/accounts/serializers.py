from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth.password_validation import validate_password

from .models import User


class LoginSerializer(TokenObtainPairSerializer):

    username_field = User.USERNAME_FIELD

    def validate(self, attrs):
        data = super().validate(attrs)

        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "full_name": self.user.full_name,
            "employee_code": self.user.employee_code,
            "role": self.user.role,
        }

        return data


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "employee_code",
            "role",
            "date_joined",
        ]
        read_only_fields = fields


class LogoutSerializer(serializers.Serializer):

    refresh = serializers.CharField()

    def validate_refresh(self, value):
        try:
            token = RefreshToken(value)

            request = self.context.get("request")

            if str(token.get("user_id")) != str(request.user.id):
                raise serializers.ValidationError(
                    "This refresh token does not belong to you."
                )

            self.token = token

            return value

        except TokenError:
            raise serializers.ValidationError("Invalid or expired refresh token.")

    def save(self, **kwargs):
        self.token.blacklist()


class EmployeeCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "employee_code",
            "password",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        password = validated_data.pop("password")

        return User.objects.create_user(
            password=password, role=User.Role.EMPLOYEE, **validated_data
        )


class EmployeeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "employee_code",
            "role",
            "is_active",
            "date_joined",
        ]
        read_only_fields = fields


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "full_name",
            "employee_code",
            "is_active",
        ]
        extra_kwargs = {
            "email": {"required": False},
            "full_name": {"required": False},
            "employee_code": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
            },
        }
