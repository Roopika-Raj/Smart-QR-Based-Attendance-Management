from django.urls import path

from .views import (
    AttendanceScanView,
    MyAttendanceView,
)

urlpatterns = [
    path(
        "scan/",
        AttendanceScanView.as_view(),
        name="attendance-scan",
    ),
    path(
        "my/",
        MyAttendanceView.as_view(),
        name="my-attendance",
    ),
]
