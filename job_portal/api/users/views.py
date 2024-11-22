from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from users.models import ApplicantProfile, EmployerProfile
from .serializers import (
    EmployerProfileSerializer,
    UserRegisterSerializer,
    ApplicantProfileSerializer,
)
from api.utils import ApiResponse


# Create your views here.
class RegisterView(APIView):
    """User Operations"""

    def post(self, request):
        try:
            serializer = UserRegisterSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return ApiResponse.success(
                    message="User registered successfully.",
                    status_code=status.HTTP_201_CREATED,
                )
            else:
                return ApiResponse.serializer_error(serializer_errors=serializer.errors)
        except Exception as e:
            return ApiResponse.error(
                message="An unexpected error occurred.",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LogoutView(APIView):
    """user logout functionality"""

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return ApiResponse.success(
                message="Logout Successfully.",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return ApiResponse.error(
                message="An unexpected error occurred.",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ApplicantProfileView(APIView):
    """Applicant Profile"""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            if ApplicantProfile.objects.filter(user=request.user).exists():
                return ApiResponse.error(
                    message="An applicant profile already exists for this user.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            elif not request.user.is_applicant:
                return ApiResponse.error(
                    message="This action requires an applicant profile.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            serializer = ApplicantProfileSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return ApiResponse.success(
                    message="Applicant Profile Created Successfully!",
                    status_code=status.HTTP_201_CREATED,
                )
            else:
                return ApiResponse.serializer_error(serializer_errors=serializer.errors)

        except Exception as e:
            return ApiResponse.error(
                message="An unexpected error occurred.",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get(self, request):
        try:
            applicant_profile = ApplicantProfile.objects.get(user=request.user)
            serializer = ApplicantProfileSerializer(applicant_profile)
            return ApiResponse.success(
                data=serializer.data,
                message="Applicant profile retrieved successfully.",
                status_code=status.HTTP_200_OK,
            )
        except ObjectDoesNotExist:
            # Handle case when the applicant profile does not exist
            return ApiResponse.error(
                message="An applicant profile does not exist for this user.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return ApiResponse.error(
                message="An unexpected error occurred.",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request):
        try:
            applicant_profile = ApplicantProfile.objects.get(user=request.user)
            serializer = ApplicantProfileSerializer(
                applicant_profile, request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return ApiResponse.success(
                    message="Applicant Profile Updated Successfully!",
                )
            else:
                return ApiResponse.serializer_error(serializer_errors=serializer.errors)

        except ObjectDoesNotExist:
            # Handle case when the applicant profile does not exist
            return ApiResponse.error(
                message="An applicant profile does not exist for this user.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return ApiResponse.error(
                message="An unexpected error occurred.",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class EmployerProfileView(APIView):
    """Applicant Profile"""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            if EmployerProfile.objects.filter(user=request.user).exists():
                return ApiResponse.error(
                    message="An employer profile already exists for this user.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            elif not request.user.is_employer:
                return ApiResponse.error(
                    message="This action requires an employer profile.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            serializer = EmployerProfileSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return ApiResponse.success(
                    message="Employer Profile Created Successfully!",
                    status_code=status.HTTP_201_CREATED,
                )
            else:
                return ApiResponse.serializer_error(serializer_errors=serializer.errors)

        except Exception as e:
            return ApiResponse.error(
                message="An unexpected error occurred.",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get(self, request):
        try:
            employer_profile = EmployerProfile.objects.get(user=request.user)
            serializer = EmployerProfileSerializer(employer_profile)
            return ApiResponse.success(
                data=serializer.data,
                message="Employer profile retrieved successfully.",
                status_code=status.HTTP_200_OK,
            )

        except ObjectDoesNotExist:
            # Handle case when the applicant profile does not exist
            return ApiResponse.error(
                message="An Employer profile does not exist for this user.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return ApiResponse.error(
                message="An unexpected error occurred.",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request):
        try:
            employer_profile = EmployerProfile.objects.get(user=request.user)
            serializer = EmployerProfileSerializer(
                employer_profile, request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return ApiResponse.success(
                    data=serializer.data,
                    message="Employer Profile Updated Successfully!",
                )
            else:
                return ApiResponse.serializer_error(serializer_errors=serializer.errors)

        except ObjectDoesNotExist:
            # Handle case when the applicant profile does not exist
            return ApiResponse.error(
                message="An Employer profile does not exist for this user.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            return ApiResponse.error(
                message="An unexpected error occurred.",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
