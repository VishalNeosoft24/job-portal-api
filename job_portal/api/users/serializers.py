from rest_framework import serializers
from users.models import User, ApplicantProfile, EmployerProfile
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.hashers import make_password


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    user_type = serializers.CharField()

    def validate_user_type(self, value):
        """Custom validation for user_type"""
        if value not in ["Applicant", "Employer"]:
            raise serializers.ValidationError("Invalid User Type")
        return value

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "password",
            "email",
            "user_type",
        ]

    def create(self, validated_data):
        user_type = validated_data.pop("user_type")
        password = validated_data.pop("password")
        user = User.objects.create(
            password=make_password(password),
            **validated_data,
        )

        if user_type == "Applicant":
            content_type = ContentType.objects.get_for_model(ApplicantProfile)
            user.content_type = content_type
        elif user_type == "Employer":
            content_type = ContentType.objects.get_for_model(EmployerProfile)
            user.content_type = content_type
        else:
            raise serializers.ValidationError("Invalid User Type")
        user.save()

        return user
