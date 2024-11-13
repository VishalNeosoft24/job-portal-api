from . import views
from django.urls import path


urlpatterns = [
    path("", views.UserAPIView.as_view(), "all_users"),
]
