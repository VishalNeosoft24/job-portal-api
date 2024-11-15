from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from jobs.models import Jobs
from .serializers import JobSerializer
from rest_framework import status
from users.models import EmployerProfile
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from .permissions import HasEmployerProfilePermission
from rest_framework.exceptions import PermissionDenied
from api.utils import ApiResponse


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
        except PermissionDenied as e:
            return ApiResponse.error(
                message=str(e),
                status_code=status.HTTP_403_FORBIDDEN,
            )

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

        except EmployerProfile.DoesNotExist:
            # Handle case when the applicant profile does not exist
            return ApiResponse.error(
                message="Employer profile not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        except Jobs.DoesNotExist:
            # Handle case where the job does not exist for this employer
            return ApiResponse.error(
                message="Job not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        except MultipleObjectsReturned:
            # Handle case when multiple profiles exist for the user (indicating a data issue)
            return ApiResponse.error(
                message="Multiple entries found, please contact support.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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

        except EmployerProfile.DoesNotExist:
            # Handle case when the applicant profile does not exist
            return ApiResponse.error(
                message="Employer profile not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        except Jobs.DoesNotExist:
            # Handle case where the job does not exist for this employer
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

        except EmployerProfile.DoesNotExist:
            # Handle case when the applicant profile does not exist
            return ApiResponse.error(
                message="Employer profile not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        except Jobs.DoesNotExist:
            # Handle case where the job does not exist for this employer
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
        except ObjectDoesNotExist:
            # Handle case when the applicant profile does not exist
            return ApiResponse.error(
                message="Job does not exist",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        except MultipleObjectsReturned:
            # Handle case when multiple profiles exist for the user (indicating a data issue)
            return ApiResponse.error(
                message="Multiple jobs found.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return ApiResponse.error(
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
