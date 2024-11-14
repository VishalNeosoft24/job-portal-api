from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import ApplicantProfile, EmployerProfile
from .serializers import (
    EmployerProfileSerializer,
    UserRegisterSerializer,
    ApplicantProfileSerializer,
)


# Create your views here.
class RegisterView(APIView):
    """User Operations"""

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(
                {"message": "User registered successfully."},
                status=status.HTTP_201_CREATED,
            )
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """user logout functionality"""

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return JsonResponse(
                {"message": "Logout Successfully"},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception as e:
            return JsonResponse(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ApplicantProfileView(APIView):
    """Applicant Profile"""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            applicant_profile = ApplicantProfile.objects.get(user=request.user)
            if applicant_profile:
                return JsonResponse(
                    {"error": "An applicant profile already exists for this user."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = ApplicantProfileSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return JsonResponse(
                    {"message": "Applicant Profile Created Successfully!"},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return JsonResponse(
                    {"error": str(serializer.errors)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            applicant_profile = ApplicantProfile.objects.filter(
                user=request.user
            ).first()
            if not applicant_profile:
                return JsonResponse(
                    {"error": "An Applicant profile not exists for this user."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = ApplicantProfileSerializer(applicant_profile)
            return JsonResponse(
                {
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            applicant_profile = ApplicantProfile.objects.filter(
                user=request.user
            ).first()
            if not applicant_profile:
                return JsonResponse(
                    {"error": "An Applicant profile not exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = ApplicantProfileSerializer(
                applicant_profile, request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(
                    {"message": "Applicant Profile Updated Successfully!"},
                    status=status.HTTP_201_CREATED,
                )
            return JsonResponse(
                {"error": str(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EmployerProfileView(APIView):
    """Applicant Profile"""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            employer_profile = EmployerProfile.objects.filter(user=request.user).first()
            if employer_profile:
                return JsonResponse(
                    {"error": "An employer profile already exists for this user."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = EmployerProfileSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return JsonResponse(
                    {"message": "Employer Profile Created Successfully!"},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return JsonResponse(
                    {"error": str(serializer.errors)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            employer_profile = EmployerProfile.objects.filter(user=request.user).first()
            if not employer_profile:
                return JsonResponse(
                    {"error": "An Employer profile not exists for this user."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = EmployerProfileSerializer(employer_profile)
            return JsonResponse(
                {
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            employer_profile = EmployerProfile.objects.filter(user=request.user).first()
            if not employer_profile:
                return JsonResponse(
                    {"error": "An Employer profile not exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = EmployerProfileSerializer(
                employer_profile, request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(
                    {"message": "Employer Profile Updated Successfully!"},
                    status=status.HTTP_201_CREATED,
                )
            return JsonResponse(
                {"error": str(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
