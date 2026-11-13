from django.urls import path

from .views import (
    LoginView,
    RefreshTokenView,
    LogoutView,
    ProfileView,
    EmployeeListCreateView,
    EmployeeDetailView,
)

urlpatterns = [
    # Authentication
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshTokenView.as_view(), name="token-refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    # Employee management
    path(
        "admin/employees/",
        EmployeeListCreateView.as_view(),
        name="employee-list-create",
    ),
    path(
        "admin/employees/<int:pk>/",
        EmployeeDetailView.as_view(),
        name="employee-detail",
    ),
]
