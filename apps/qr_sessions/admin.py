from django.contrib import admin
from .models import QRSession


@admin.register(QRSession)
class QRSessionAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "status",
        "starts_at",
        "ends_at",
        "created_by",
    )

    list_filter = ("status",)
    search_fields = ("title",)
    readonly_fields = (
        "current_nonce",
        "qr_expires_at",
        "created_at",
        "updated_at",
    )
