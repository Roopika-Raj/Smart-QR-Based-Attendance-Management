from django.urls import path

from .views import (
    QRSessionListCreateView,
    QRSessionDetailView,
    CurrentQRView,
    RefreshQRView,
    CloseQRSessionView,
)

urlpatterns = [
    path(
        "",
        QRSessionListCreateView.as_view(),
        name="qr-session-list-create",
    ),
    path(
        "<int:pk>/",
        QRSessionDetailView.as_view(),
        name="qr-session-detail",
    ),
    path(
        "<int:pk>/current-qr/",
        CurrentQRView.as_view(),
        name="current-qr",
    ),
    path(
        "<int:pk>/refresh-qr/",
        RefreshQRView.as_view(),
        name="refresh-qr",
    ),
    path(
        "<int:pk>/close/",
        CloseQRSessionView.as_view(),
        name="close-qr-session",
    ),
]
