from django.contrib import admin

from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "employee",
        "session",
        "check_in_at",
        "check_out_at",
    )

    search_fields = (
        "employee__full_name",
        "employee__email",
        "employee__employee_code",
        "session__title",
    )

    list_filter = ("session",)

    readonly_fields = (
        "employee",
        "session",
        "check_in_at",
        "check_in_latitude",
        "check_in_longitude",
        "check_out_at",
        "check_out_latitude",
        "check_out_longitude",
    )
