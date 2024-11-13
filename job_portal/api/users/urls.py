from . import views
from django.urls import path


urlpatterns = [
    path("", views.UserAPIView.as_view(), name="all_users"),
]
