import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class QRSession(models.Model):

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        CLOSED = "CLOSED", "Closed"

    title = models.CharField(max_length=150)

    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )

    current_nonce = models.UUIDField(default=uuid.uuid4, editable=False)

    qr_expires_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_qr_sessions",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "qr_sessions"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def is_currently_active(self):
        now = timezone.now()

        return (
            self.status == self.Status.ACTIVE and self.starts_at <= now < self.ends_at
        )
