from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdminRole, IsEmployeeRole
from apps.qr_sessions.models import QRSession
from apps.qr_sessions.services import validate_qr_token

from .models import Attendance
from .serializers import (
    AttendanceScanSerializer,
    AttendanceSerializer,
)


class AttendanceScanView(APIView):

    permission_classes = [IsEmployeeRole]

    def post(self, request):

        input_serializer = AttendanceScanSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        data = input_serializer.validated_data

        # Validate the QR token first.
        session = validate_qr_token(data["qr_payload"])

        if session is None:
            return Response(
                {"success": False, "message": "Invalid or expired QR code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():

                # Lock the session and revalidate the QR token.
                locked_session = QRSession.objects.select_for_update().get(
                    pk=session.pk
                )

                session = validate_qr_token(data["qr_payload"])

                if session is None:
                    return Response(
                        {"success": False, "message": "Invalid or expired QR code."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if session.pk != locked_session.pk:
                    return Response(
                        {"success": False, "message": "Invalid QR session."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                now = timezone.now()

                if data["action"] == "CHECK_IN":

                    attendance, created = Attendance.objects.get_or_create(
                        employee=request.user,
                        session=locked_session,
                        defaults={
                            "check_in_at": now,
                            "check_in_latitude": data["latitude"],
                            "check_in_longitude": data["longitude"],
                        },
                    )

                    if not created:
                        return Response(
                            {
                                "success": False,
                                "message": "You have already checked in for this session.",
                            },
                            status=status.HTTP_409_CONFLICT,
                        )

                    return Response(
                        {
                            "success": True,
                            "message": "Check-in successful.",
                            "data": AttendanceSerializer(attendance).data,
                        },
                        status=status.HTTP_201_CREATED,
                    )

                # CHECK_OUT
                attendance = (
                    Attendance.objects.select_for_update()
                    .filter(employee=request.user, session=locked_session)
                    .first()
                )

                if attendance is None:
                    return Response(
                        {
                            "success": False,
                            "message": "Please check in before checking out.",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if attendance.check_out_at is not None:
                    return Response(
                        {
                            "success": False,
                            "message": "You have already checked out for this session.",
                        },
                        status=status.HTTP_409_CONFLICT,
                    )

                attendance.check_out_at = now
                attendance.check_out_latitude = data["latitude"]
                attendance.check_out_longitude = data["longitude"]

                attendance.save(
                    update_fields=[
                        "check_out_at",
                        "check_out_latitude",
                        "check_out_longitude",
                    ]
                )

                return Response(
                    {
                        "success": True,
                        "message": "Check-out successful.",
                        "data": AttendanceSerializer(attendance).data,
                    },
                    status=status.HTTP_200_OK,
                )

        except IntegrityError:
            return Response(
                {"success": False, "message": "Attendance has already been recorded."},
                status=status.HTTP_409_CONFLICT,
            )


class MyAttendanceView(generics.ListAPIView):

    permission_classes = [IsEmployeeRole]
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        return Attendance.objects.filter(employee=self.request.user).select_related(
            "employee", "session"
        )


class AdminAttendanceListView(generics.ListAPIView):

    permission_classes = [IsAdminRole]
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        return Attendance.objects.select_related("employee", "session").all()
