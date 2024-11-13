from django.urls import path, include


urlpatterns = [
    path("users/", include("api.user_api.urls")),
]
