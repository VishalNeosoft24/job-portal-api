from django.contrib import admin
from .models import User, ApplicantProfile, Skill

# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "first_name", "last_name", "username", "email"]
    search_fields = ["username", "email", "id"]
    list_filter = ["last_login", "date_joined"]


@admin.register(ApplicantProfile)
class ApplicantProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "full_name"]


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
    ]
