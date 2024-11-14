from . import views
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView


urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path(
        "profile/applicant/",
        views.ApplicantProfileView.as_view(),
        name="applicant_profile",
    ),
    path(
        "profile/employer/",
        views.EmployerProfileView.as_view(),
        name="employer_profile",
    ),
]
