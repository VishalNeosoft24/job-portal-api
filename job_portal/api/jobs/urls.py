from django.urls import path
from . import views


urlpatterns = [
    # Jobs
    path("job/", views.JobCreateRetrieveView.as_view(), name="job"),
    path("employer/job/", views.RetrieveEmployerJob.as_view(), name="employer_job"),
    path(
        "job/<int:job_id>/",
        views.JobRetrieveUpdateDeleteView.as_view(),
        name="job_details",
    ),
    # JobApplication
    path(
        "job-application/", views.JobApplicationView.as_view(), name="job_application"
    ),
    path(
        "job-application/<int:job_application_id>/",
        views.JobApplicationView.as_view(),
        name="job_application_",
    ),
]
