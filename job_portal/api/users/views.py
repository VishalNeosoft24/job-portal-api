from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegisterSerializer


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
                {"message": "Logout Successfully"}, status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProtectedView(APIView):
    authentication_classes = [JWTAuthentication]  # Use JWT authentication
    permission_classes = [permissions.IsAuthenticated]  # Allow only authenticated users

    def get(self, request):
        content = {"message": "Successful!"}
        return JsonResponse(content)
