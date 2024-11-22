from .models import JobApplication, JobApplicationAudit
from api.utils import ApiResponse
from rest_framework import status


class JobApplicationAuditLogs:

    def __init__(self, job_application: JobApplication):
        self.job_application = job_application

    def add_audit_logs(self, job_status, updated_by, notes=""):
        try:

            job_application_audit = JobApplicationAudit.objects.create(
                job_application=self.job_application,
                status=job_status,
                notes=notes,
                updated_by=updated_by,
            )
            job_application_audit.save()

        except Exception as e:
            return ApiResponse.error(
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
