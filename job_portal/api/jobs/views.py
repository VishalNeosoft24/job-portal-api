from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from jobs.models import Jobs, JobApplication
from .serializers import JobApplicationSerializer, JobSerializer
from rest_framework import status
from users.models import EmployerProfile, ApplicantProfile
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from .permissions import HasEmployerProfilePermission
from rest_framework.exceptions import PermissionDenied
from api.utils import ApiResponse
from jobs.utils import JobApplicationAuditLogs


class JobCreateRetrieveView(APIView):
    """JobView"""

    authentication_classes = [JWTAuthentication]

    @permission_classes([IsAuthenticated, HasEmployerProfilePermission])
    def post(self, request):
        try:
            serializer = JobSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.save()
                return ApiResponse.success(
                    message="New Job Created!",
                    status_code=status.HTTP_201_CREATED,
                )
            else:
                return ApiResponse.serializer_error(serializer_errors=serializer.errors)
        except Exception as e:
            return ApiResponse.error(
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get(self, request):
        try:
            jobs = Jobs.objects.filter(is_active=True).all()
            serializer = JobSerializer(jobs, many=True)
            return ApiResponse.success(
                data=serializer.data,
                message="Jobs retrieved successfully.",
                status_code=status.HTTP_200_OK,
            )

        except Exception as e:
            return ApiResponse.error(
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class JobRetrieveUpdateDeleteView(APIView):
    """Job Detail View"""

    permission_classes = [IsAuthenticated, HasEmployerProfilePermission]
    authentication_classes = [JWTAuthentication]

    def get(self, request, job_id):
        try:
            # Fetch the employer profile for the logged-in user
            employer = EmployerProfile.objects.get(user=request.user)

            # Check for the specific job related to this employer
            job = Jobs.objects.get(employer=employer, id=job_id)

            serializer = JobSerializer(job)
            return ApiResponse.success(
                data=serializer.data,
                message="Jobs Details retrieved successfully.",
                status_code=status.HTTP_200_OK,
            )
        except Jobs.DoesNotExist:
            return ApiResponse.error(
                message="Job not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return ApiResponse.error(
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, job_id):
        try:
            # Fetch the employer profile for the logged-in user
            employer = EmployerProfile.objects.get(user=request.user)

            # Check for the specific job related to this employer
            job = Jobs.objects.get(employer=employer, id=job_id)

            serializer = JobSerializer(job, request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return ApiResponse.success(
                    data=serializer.data,
                    message="Job Updated Successfully",
                )
            else:
                return ApiResponse.serializer_error(serializer_errors=serializer.errors)

        except Jobs.DoesNotExist:
            return ApiResponse.error(
                message="Job not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return ApiResponse.error(
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, job_id):
        try:
            # Fetch the employer profile for the logged-in user
            employer = EmployerProfile.objects.get(user=request.user)

            # Check for the specific job related to this employer
            job = Jobs.objects.get(employer=employer, id=job_id)

            job.delete()
            return ApiResponse.success(
                message="Job Deleted Successfully",
            )

        except Jobs.DoesNotExist:
            return ApiResponse.error(
                message="Job not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return ApiResponse.error(
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RetrieveEmployerJob(APIView):
    """Retrieve Employer job only"""

    permission_classes = [IsAuthenticated, HasEmployerProfilePermission]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        try:
            employer = EmployerProfile.objects.get(user=request.user)
            jobs = Jobs.objects.filter(employer=employer).all()
            serializer = JobSerializer(jobs, many=True)
            return ApiResponse.success(
                data=serializer.data,
                message="Jobs retrieved successfully.",
                status_code=status.HTTP_200_OK,
            )

        except Exception as e:
            return ApiResponse.error(
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class JobApplicationView(APIView):
    "JobApplicationCreateRetrieveView"

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            serializer = JobApplicationSerializer(data=request.data)
            if serializer.is_valid():
                job_application = serializer.save()

                job_application_log = JobApplicationAuditLogs(job_application)
                job_application_log.add_audit_logs(
                    job_status=job_application.status,
                    updated_by=request.user,
                    notes="Job Applied",
                )
                return ApiResponse.success(
                    message="New JobApplication Created!",
                    status_code=status.HTTP_201_CREATED,
                )
            else:
                return ApiResponse.serializer_error(serializer_errors=serializer.errors)

        except Exception as e:
            return ApiResponse.error(
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get(self, request):
        try:
            applicant = ApplicantProfile.objects.get(user=request.user)
            job_applications = JobApplication.objects.filter(applicant=applicant).all()
            serializer = JobApplicationSerializer(job_applications, many=True)
            return ApiResponse.success(
                data=serializer.data,
                message="JobApplications retrieved successfully.",
                status_code=status.HTTP_200_OK,
            )
        except ApplicantProfile.DoesNotExist:
            return ApiResponse.error(
                message="Applicant profile not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return ApiResponse.error(
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, job_application_id):
        try:
            job_application = JobApplication.objects.get(id=job_application_id)
            job_application.delete()
            return ApiResponse.success(
                message="Job Application Deleted Successfully",
            )
        except JobApplication.DoesNotExist:
            return ApiResponse.error(
                message="Job Application not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return ApiResponse.error(
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
