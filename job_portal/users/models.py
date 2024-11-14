from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Create your models here.


class BaseModel(models.Model):
    """
    Abstract base model to add common timestamp fields to all models.

    Fields:
        created_at (DateTimeField): The timestamp when the record was created.
        updated_at (DateTimeField): The timestamp when the record was last updated.
        deleted_at (DateTimeField): Optional timestamp indicating when the record was deleted.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser, adding user roles.

    Fields:
        is_applicant (BooleanField): Flag to identify if the user is an applicant.
        is_employer (BooleanField): Flag to identify if the user is an employer.
    """

    is_applicant = models.BooleanField(default=False)
    is_employer = models.BooleanField(default=False)


class ApplicantProfile(BaseModel):
    """
    Profile model for users who are applicants.

    Fields:
        user (OneToOneField): Reference to the User model (applicant).
        full_name (CharField): Full name of the applicant.
        phone_number (CharField): Contact number of the applicant.
        address (TextField): Residential address of the applicant.
        resume_file (FileField): Uploaded resume of the applicant.
        skills (ManyToManyField): Set of skills the applicant possesses.
        profile_complete (BooleanField): Indicates if the profile setup is complete.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="applicant_profile"
    )
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    resume_file = models.FileField(upload_to="resumes/")
    skills = models.ManyToManyField("Skill", related_name="applicants")
    profile_complete = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class EmployerProfile(BaseModel):
    """
    Profile model for users who are employers.

    Fields:
        user (OneToOneField): Reference to the User model (employer).
        company_name (CharField): Name of the employer's company.
        company_website (URLField): Website of the employer's company.
        location (CharField): Location of the employer's company.
        description (TextField): Description or additional information about the employer.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="employer_profile"
    )
    company_name = models.CharField(max_length=100)
    company_website = models.URLField()
    location = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.company_name


class Skill(BaseModel):
    """
    Model to represent a skill.

    Fields:
        name (CharField): Name of the skill.
    """

    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
