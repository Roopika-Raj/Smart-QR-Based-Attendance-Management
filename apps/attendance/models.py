from django.conf import settings
from django.db import models


class Attendance(models.Model):

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="attendance_records",
    )

    session = models.ForeignKey(
        "qr_sessions.QRSession",
        on_delete=models.PROTECT,
        related_name="attendance_records",
    )

    check_in_at = models.DateTimeField()

    check_in_latitude = models.DecimalField(max_digits=9, decimal_places=6)

    check_in_longitude = models.DecimalField(max_digits=9, decimal_places=6)

    check_out_at = models.DateTimeField(null=True, blank=True)

    check_out_latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )

    check_out_longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )

    class Meta:
        db_table = "attendance"
        ordering = ["-check_in_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "session"],
                name="unique_employee_session_attendance",
            )
        ]

    def __str__(self):
        return f"{self.employee} - {self.session}"
