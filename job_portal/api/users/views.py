from django.http import JsonResponse
from rest_framework.views import APIView


# Create your views here.
class UserAPIView(APIView):
    """User Operations"""

    def get(self, request):
        return JsonResponse({"data": "working"})
