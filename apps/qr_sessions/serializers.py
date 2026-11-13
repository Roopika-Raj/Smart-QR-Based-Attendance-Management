from django.utils import timezone
from rest_framework import serializers

from .models import QRSession


class QRSessionSerializer(serializers.ModelSerializer):

    created_by_name = serializers.CharField(
        source="created_by.full_name",
        read_only=True,
    )

    class Meta:
        model = QRSession

        fields = [
            "id",
            "title",
            "starts_at",
            "ends_at",
            "status",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "status",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        now = timezone.now()

        starts_at = attrs.get(
            "starts_at",
            getattr(self.instance, "starts_at", None),
        )

        ends_at = attrs.get(
            "ends_at",
            getattr(self.instance, "ends_at", None),
        )

        if starts_at and starts_at > now:
            raise serializers.ValidationError(
                {"starts_at": "The session must start now or in the past."}
            )

        if ends_at and ends_at <= now:
            raise serializers.ValidationError(
                {"ends_at": "The session end time must be in the future."}
            )

        if starts_at and ends_at and ends_at <= starts_at:
            raise serializers.ValidationError(
                {"ends_at": "End time must be later than start time."}
            )

        return attrs

    def create(self, validated_data):
        return QRSession.objects.create(
            created_by=self.context["request"].user,
            **validated_data,
        )
