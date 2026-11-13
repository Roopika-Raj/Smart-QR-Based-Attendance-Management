from rest_framework import serializers
from django.db import models
from .models import Attendance


class AttendanceScanSerializer(serializers.Serializer):

    class Action(models.TextChoices):
        CHECK_IN = "CHECK_IN", "Check In"
        CHECK_OUT = "CHECK_OUT", "Check Out"

    qr_payload = serializers.CharField()

    action = serializers.ChoiceField(choices=Action.choices)

    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)

    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)

    def validate_latitude(self, value):
        if not -90 <= value <= 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90.")
        return value

    def validate_longitude(self, value):
        if not -180 <= value <= 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180.")
        return value


class AttendanceSerializer(serializers.ModelSerializer):

    employee_name = serializers.CharField(source="employee.full_name", read_only=True)

    employee_code = serializers.CharField(
        source="employee.employee_code", read_only=True
    )

    session_title = serializers.CharField(source="session.title", read_only=True)

    class Meta:
        model = Attendance

        fields = [
            "id",
            "employee",
            "employee_name",
            "employee_code",
            "session",
            "session_title",
            "check_in_at",
            "check_in_latitude",
            "check_in_longitude",
            "check_out_at",
            "check_out_latitude",
            "check_out_longitude",
        ]

        read_only_fields = fields
