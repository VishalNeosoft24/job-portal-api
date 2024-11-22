from django.contrib import admin
from .models import JobApplicationAudit, Jobs, JobApplication

# Register your models here.


@admin.register(Jobs)
class JobsAdmin(admin.ModelAdmin):
    """Jobs Admin"""

    list_display = [
        "id",
        "employer",
        "job_title",
        "description",
        "location",
        "salary_min",
        "salary_max",
        "job_type",
        "experience_level",
        "posted_date",
        "is_active",
    ]
    list_filter = [
        "job_title",
        "location",
        "experience_level",
        "posted_date",
        "is_active",
    ]


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    """JobApplicationAdmin"""

    list_display = [
        "id",
        "applicant",
        "job_listing",
        "status",
        "applied_date",
    ]
    list_filter = ["status"]


@admin.register(JobApplicationAudit)
class JobApplicationAuditAdmin(admin.ModelAdmin):
    list_display = [
        "job_application",
        "status",
        "notes",
        "updated_by",
        "updated_at",
    ]
