from rest_framework import serializers
from users.models import EmployerProfile, User, ApplicantProfile, Skill
from django.contrib.auth.hashers import make_password
import re


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    user_type = serializers.CharField(write_only=True)

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
            user.is_applicant = True
        elif user_type == "Employer":
            user.is_employer = True
        else:
            raise serializers.ValidationError("Invalid User Type")
        user.save()

        return user


class ApplicantProfileSerializer(serializers.ModelSerializer):
    """ApplicantProfileSerializer"""

    user = UserRegisterSerializer()
    skills = serializers.PrimaryKeyRelatedField(queryset=Skill.objects.all(), many=True)

    class Meta:
        model = ApplicantProfile
        fields = [
            "user",
            "phone_number",
            "address",
            "resume_file",
            "skills",
            "profile_complete",
        ]

    def validate_resume_file(self, value):
        if value.content_type != "application/pdf":
            raise serializers.ValidationError(
                "Only PDF files are allowed for the resume."
            )
        return value

    def validate_phone_number(self, value):
        if not re.match(r"^\d{10}$", str(value)):
            raise serializers.ValidationError("Phone number must be exactly 10 digits.")
        return value

    def create(self, validated_data):
        skills_data = validated_data.pop("skills")
        user = validated_data.pop("user")
        profile = ApplicantProfile.objects.create(user=user, **validated_data)
        profile.skills.set(skills_data)
        profile.save()

        return profile

    def update(self, instance, validated_data):
        skills_data = validated_data.pop("skills", [])

        for key, val in validated_data.items():
            setattr(instance, key, val)

        instance.skills.set(skills_data)
        instance.save()

        return instance


class EmployerProfileSerializer(serializers.ModelSerializer):
    """EmployerProfileSerializer"""

    user = UserRegisterSerializer()

    class Meta:
        model = EmployerProfile
        fields = [
            "user",
            "company_name",
            "company_website",
            "location",
            "description",
        ]

    def create(self, validated_data):
        user = validated_data.pop("user")
        profile = EmployerProfile.objects.create(user=user, **validated_data)
        profile.save()
        return profile
