from . import views
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView


urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("protected-view/", views.ProtectedView.as_view(), name="protected-view"),
]
