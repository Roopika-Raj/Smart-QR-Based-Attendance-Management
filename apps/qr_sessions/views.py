import uuid

from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.accounts.permissions import IsAdminRole

from .models import QRSession
from .serializers import QRSessionSerializer
from .services import (
    rotate_qr_token,
    ensure_current_qr_token,
    build_qr_response,
)


class QRSessionListCreateView(generics.ListCreateAPIView):

    permission_classes = [IsAdminRole]
    serializer_class = QRSessionSerializer

    def get_queryset(self):
        return QRSession.objects.select_related("created_by").all()

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = serializer.save()

        try:
            token = rotate_qr_token(session)
        except ValueError as exc:
            session.delete()
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "success": True,
                "message": "Attendance session created successfully.",
                "session": self.get_serializer(session).data,
                "qr": build_qr_response(session, token),
            },
            status=status.HTTP_201_CREATED,
        )


class QRSessionDetailView(generics.RetrieveDestroyAPIView):

    permission_classes = [IsAdminRole]
    serializer_class = QRSessionSerializer

    def get_queryset(self):
        return QRSession.objects.select_related("created_by").all()

    def destroy(self, request, *args, **kwargs):
        session = self.get_object()

        if session.attendance_records.exists():
            return Response(
                {
                    "detail": (
                        "This session cannot be deleted because attendance "
                        "records are associated with it."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().destroy(request, *args, **kwargs)


class CurrentQRView(APIView):

    permission_classes = [IsAdminRole]

    def get(self, request, pk):

        session = get_object_or_404(QRSession, pk=pk)

        try:
            token = ensure_current_qr_token(session)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "success": True,
                "qr": build_qr_response(session, token),
            }
        )


class RefreshQRView(APIView):

    permission_classes = [IsAdminRole]

    def post(self, request, pk):

        session = get_object_or_404(QRSession, pk=pk)

        try:
            token = rotate_qr_token(session)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "success": True,
                "message": "QR token refreshed successfully.",
                "qr": build_qr_response(session, token),
            }
        )


class CloseQRSessionView(APIView):

    permission_classes = [IsAdminRole]

    def post(self, request, pk):

        session = get_object_or_404(QRSession, pk=pk)

        if session.status == QRSession.Status.CLOSED:
            return Response(
                {"detail": "This session is already closed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session.status = QRSession.Status.CLOSED
        session.current_nonce = uuid.uuid4()
        session.qr_expires_at = None

        session.save(
            update_fields=[
                "status",
                "current_nonce",
                "qr_expires_at",
                "updated_at",
            ]
        )

        return Response(
            {
                "success": True,
                "message": "Attendance session closed successfully.",
            }
        )
