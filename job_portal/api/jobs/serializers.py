from rest_framework import serializers
from jobs.models import Jobs
from users.models import Skill, EmployerProfile


class JobSerializer(serializers.ModelSerializer):
    """Job Serializer"""

    required_skills = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(), many=True
    )

    class Meta:
        model = Jobs
        fields = [
            "id",
            "job_title",
            "description",
            "location",
            "salary_min",
            "salary_max",
            "job_type",
            "required_skills",
            "experience_level",
            "posted_date",
            "is_active",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        employer = EmployerProfile.objects.get(user=request.user)
        required_skills = validated_data.pop("required_skills")
        job = Jobs.objects.create(employer=employer, **validated_data)
        job.required_skills.set(required_skills)
        job.save()

        return job

    def update(self, instance, validated_data):
        required_skills = validated_data.pop("required_skills", [])

        for key, val in validated_data.items():
            setattr(instance, key, val)

        instance.required_skills.set(required_skills)
        instance.save()
        return instance
