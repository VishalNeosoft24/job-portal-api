from django.db import models
from django.db import models
from users.models import EmployerProfile, Skill, ApplicantProfile, User, BaseModel


# Create your models here.
class Jobs(BaseModel):
    """
    Model to represent a job listing created by an employer.

    Fields:
        employer (ForeignKey): Reference to the EmployerProfile who posted the job.
        job_title (CharField): Title of the job position.
        description (TextField): Detailed description of the job responsibilities.
        location (CharField): Location where the job is based.
        salary_min (DecimalField): Minimum salary offered for the position.
        salary_max (DecimalField): Maximum salary offered for the position.
        job_type (CharField): Type of job (e.g., Full-Time, Part-Time, Contract).
        required_skills (ManyToManyField): Skills required for the job.
        experience_level (CharField): Level of experience required for the job.
        posted_date (DateTimeField): Date when the job was posted.
        is_active (BooleanField): Status indicating if the job is currently active.
    """

    JOB_TYPE_CHOICES = [("FT", "Full-Time"), ("PT", "Part-Time"), ("CT", "Contract")]
    EXPERIENCE_LEVEL_CHOICES = [
        ("entry", "Entry"),
        ("mid", "Mid"),
        ("senior", "Senior"),
    ]

    employer = models.ForeignKey(
        EmployerProfile, on_delete=models.CASCADE, related_name="job_listings"
    )
    job_title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2)
    job_type = models.CharField(
        max_length=50,
        choices=JOB_TYPE_CHOICES,
    )
    required_skills = models.ManyToManyField(Skill, related_name="job_listings")
    experience_level = models.CharField(
        max_length=50,
        choices=EXPERIENCE_LEVEL_CHOICES,
    )
    posted_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.job_title


class JobApplication(BaseModel):
    """
    Model to represent an application submitted by an applicant for a job.

    Fields:
        applicant (ForeignKey): Reference to the ApplicantProfile submitting the application.
        job_listing (ForeignKey): Reference to the Jobs model for the applied job.
        status (CharField): Current status of the application (e.g., Applied, Shortlisted, etc.).
        applied_date (DateTimeField): Date when the application was submitted.
    """

    STATUS_CHOICES = [
        ("applied", "Applied"),
        ("shortlisted", "Shortlisted"),
        ("interview", "Interview"),
        ("rejected", "Rejected"),
        ("hired", "Hired"),
        ("hold", "Hold"),
    ]
    applicant = models.ForeignKey(
        ApplicantProfile, on_delete=models.CASCADE, related_name="applications"
    )
    job_listing = models.ForeignKey(
        Jobs, on_delete=models.CASCADE, related_name="applications"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="applied",
    )
    applied_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.applicant.user.username} - {self.job_listing.job_title}"


class Notification(BaseModel):
    """
    Model to represent a notification sent to a user.

    Fields:
        user (ForeignKey): Reference to the User who receives the notification.
        message (TextField): Content of the notification message.
        is_read (BooleanField): Status indicating if the notification has been read.
        created_at (DateTimeField): Date when the notification was created.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
