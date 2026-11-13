from django.urls import path

from .views import AdminAttendanceListView

urlpatterns = [
    path(
        "",
        AdminAttendanceListView.as_view(),
        name="admin-attendance-list",
    ),
]
