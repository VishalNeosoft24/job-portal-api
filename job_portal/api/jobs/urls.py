from django.urls import path
from . import views


urlpatterns = [
    path("job/", views.JobCreateRetrieveView.as_view(), name="job"),
    path("employer/job/", views.RetrieveEmployerJob.as_view(), name="job"),
    path("job/<int:job_id>/", views.JobRetrieveUpdateDeleteView.as_view(), name="job"),
]
