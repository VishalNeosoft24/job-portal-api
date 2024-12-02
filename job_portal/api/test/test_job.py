from unittest.mock import patch

from django.urls import reverse
from faker import Faker
from jobs.models import JobApplication, Jobs
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.test import APITestCase
from users.models import ApplicantProfile, EmployerProfile, Skill, User

fake = Faker()


class JobTestSetup(APITestCase):
    """Job Testcases"""

    def setUp(self):
        """"""
        self.register_url = reverse("register")
        self.token_url = reverse("token_obtain_pair")
        self.applicant_profile_url = reverse("applicant_profile")
        self.employer_profile_url = reverse("employer_profile")

        self.job_url = reverse("job")

        self.job_valid_data = {
            "job_title": "Software Engineer",
            "description": "We are looking for a skilled software engineer to join our team. The ideal candidate will be proficient in Python, Django, and web development.",
            "location": "New York, NY",
            "salary_min": 70000,
            "salary_max": 120000,
            "job_type": "FT",
            "experience_level": "mid",
            "posted_date": "2024-11-14",
            "is_active": True,
        }

        return super().setUp()

    def create_user(self, type=None):
        """"""
        self.user_common_data = {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "username": fake.user_name(),
            "password": fake.password(),
            "email": fake.email(),
        }

        if type == "applicant":
            self.user_type = {
                **self.user_common_data,
                "user_type": "Applicant",
            }
        elif type == "employer":
            self.user_type = {
                **self.user_common_data,
                "user_type": "Employer",
            }

        response = self.client.post(self.register_url, data=self.user_type)
        self.assertEqual(response.status_code, 201)

        # Obtain access token
        token_res = self.client.post(
            self.token_url,
            data={
                "username": self.user_type["username"],
                "password": self.user_type["password"],
            },
        )
        self.assertEqual(token_res.status_code, status.HTTP_200_OK)
        self.access_token = token_res.data["access"]
        self.refresh_token = token_res.data["refresh"]

        #  set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def create_applicant_profile(self):
        """"""
        self.create_user(type="applicant")

        self.applicant_profile_data = {
            "phone_number": "1245125412",
            "address": fake.address(),
            "skills": [1, 2, 3],
            "profile_complete": True,
        }

        self.employer_profile_data = {
            "company_name": fake.company(),
            "company_website": fake.url(),
            "location": fake.city(),
            "description": fake.address(),
        }

        Skill.objects.bulk_create(
            [Skill(name="python"), Skill(name="django"), Skill(name="drf")]
        )
        with open(
            "/home/neosoft/Downloads/Darsh_Modi1731414878-DB Crop.pdf", "rb"
        ) as resume:
            response = self.client.post(
                self.applicant_profile_url,
                data={**self.applicant_profile_data, "resume_file": resume},
                format="multipart",
            )
        self.assertEquals(response.status_code, 201)

    def create_employer_profile(self):
        """"""
        self.create_user(type="employer")

        self.employer_profile_data = {
            "company_name": fake.company(),
            "company_website": fake.url(),
            "location": fake.city(),
            "description": fake.address(),
        }

        # Create employer profile
        response = self.client.post(
            self.employer_profile_url, data=self.employer_profile_data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(
            response.data["message"], "Employer Profile Created Successfully!"
        )

    def create_skills(self, skill_names=["python", "django", "drf"]):
        """Create skills dynamically and return their IDs."""
        skill_objects = [
            Skill(name=name) for name in skill_names
        ]  # Create skill instances
        Skill.objects.bulk_create(skill_objects)  # Save to the database
        return list(
            Skill.objects.filter(name__in=skill_names).values_list("id", flat=True)
        )  # Fetch IDs

    def test_create_job_with_success(self):
        """Create a job with valid data"""
        self.create_employer_profile()
        skill_ids = self.create_skills()
        self.job_valid_data["required_skills"] = skill_ids

        response = self.client.post(self.job_url, data=self.job_valid_data)
        self.assertEqual(response.status_code, 201)

    def test_create_job_with_invalid_data(self):
        """Attempt to create a job with invalid data"""
        self.create_employer_profile()
        invalid_job_data = {**self.job_valid_data, "job_title": ""}  # Missing title
        response = self.client.post(self.job_url, data=invalid_job_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("job_title", response.data["errors"])

    def test_create_job_without_authentication(self):
        """Ensure unauthenticated users cannot create jobs"""
        response = self.client.post(self.job_url, data=self.job_valid_data)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data["status"])

    def test_create_job_without_permission(self):
        """Attempt to create a job without proper permissions"""

        # Create a user with the applicant role
        self.create_user(type="applicant")  # Applicants should not have EmployerProfile
        skill_ids = self.create_skills()
        self.job_valid_data["required_skills"] = skill_ids

        # Attempt to post job data
        response = self.client.post(self.job_url, data=self.job_valid_data)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch("jobs.models.Jobs.save")
    def test_internal_server_error_job_create(self, mock_create_job):
        """Test unexpected exception handling in job application retrieval"""
        # Simulate an unexpected error during the request
        mock_create_job.side_effect = Exception("Something went wrong.")

        """Simulate an unexpected error during job creation"""
        self.create_employer_profile()
        skill_ids = self.create_skills()
        self.job_valid_data["required_skills"] = skill_ids

        response = self.client.post(self.job_url, data=self.job_valid_data)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_get_jobs(self):
        """Retrieve active jobs"""
        self.create_employer_profile()
        skill_ids = self.create_skills()
        self.job_valid_data["required_skills"] = skill_ids
        self.client.post(self.job_url, data=self.job_valid_data)

        response = self.client.get(self.job_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_job_with_unexpected_error(self):
        """Simulate an unexpected error during job retrieval with a GET request"""

        # Create an employer profile and add job data (simulated)
        self.create_employer_profile()
        skill_ids = self.create_skills()
        self.job_valid_data["required_skills"] = skill_ids

        # Simulate an unexpected error when fetching the job (Job.objects.get)
        with patch("jobs.models.Jobs.objects.filter") as mocked_get:
            mocked_get.side_effect = Exception("Something went wrong!")

            # Simulate a GET request to retrieve the job
            response = self.client.get(self.job_url)  # Simulate a GET request

            # Assert that the response status is 500 Internal Server Error
            self.assertEqual(
                response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR
            )

            # Assert that the error message contains "An unexpected error occurred"
            self.assertIn("An unexpected error occurred", response.data["message"])


class JobRetrieveUpdateDeleteViewTest(APITestCase):
    """"""

    def setUp(self):
        # Setup a test employer and job for the user
        self.register_url = reverse("register")
        self.token_url = reverse("token_obtain_pair")
        self.employer_profile_url = reverse("employer_profile")
        self.applicant_profile_url = reverse("applicant_profile")

        self.create_employer_profile()
        self.job = self.create_job()  # Helper method to create a job
        self.job_url = f"http://127.0.0.1:8000/api/jobs/job/{self.job.id}/"
        self.employer_job = f"http://127.0.0.1:8000/api/jobs/employer/job/"
        self.job_application = f"http://127.0.0.1:8000/api/jobs/job-application/"

    def create_user(self, type=None):
        """"""
        self.user_common_data = {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "username": fake.user_name(),
            "password": fake.password(),
            "email": fake.email(),
        }

        if type == "applicant":
            self.user_type = {
                **self.user_common_data,
                "user_type": "Applicant",
            }
        elif type == "employer":
            self.user_type = {
                **self.user_common_data,
                "user_type": "Employer",
            }

        response = self.client.post(self.register_url, data=self.user_type)
        self.assertEqual(response.status_code, 201)

        # Obtain access token
        token_res = self.client.post(
            self.token_url,
            data={
                "username": self.user_type["username"],
                "password": self.user_type["password"],
            },
        )
        self.assertEqual(token_res.status_code, status.HTTP_200_OK)
        self.access_token = token_res.data["access"]
        self.refresh_token = token_res.data["refresh"]

        #  set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        user = User.objects.get(username=self.user_type["username"])
        return user

    def create_employer_profile(self):
        """Helper method to create an employer profile"""
        user = self.create_user(type="employer")

        self.employer_profile_data = {
            "company_name": fake.company(),
            "company_website": fake.url(),
            "location": fake.city(),
            "description": fake.address(),
        }

        # Create employer profile

        profile = EmployerProfile.objects.create(
            user=user, **self.employer_profile_data
        )
        return profile

    def create_applicant_profile(self):
        """Helper method to create an applicant profile"""
        user = self.create_user(type="applicant")

        self.applicant_profile_data = {
            "phone_number": "1245125412",
            "address": fake.address(),
            "profile_complete": True,
        }
        # Create applicant profile without skills initially
        profile = ApplicantProfile.objects.create(
            user=user, **self.applicant_profile_data
        )

        # Add skills using set()
        skill_ids = self.create_skills()
        profile.skills.set(skill_ids)  # Use .set() for Many-to-Many relationships

        import os

        from django.core.files.uploadedfile import SimpleUploadedFile

        # Provide a file object with a proper filename
        resume_path = "/home/neosoft/Downloads/Darsh_Modi1731414878-DB Crop.pdf"
        resume_filename = os.path.basename(resume_path)

        with open(resume_path, "rb") as f:
            resume = SimpleUploadedFile(
                resume_filename, f.read(), content_type="application/pdf"
            )

        # Save the resume file correctly
        profile.resume_file.save(resume.name, resume)
        profile.save()
        return profile

    def create_skills(self, skill_names=["python", "django", "drf"]):
        """Create skills dynamically and return their IDs."""
        skill_objects = [
            Skill(name=name) for name in skill_names
        ]  # Create skill instances
        Skill.objects.bulk_create(skill_objects)  # Save to the database
        return list(
            Skill.objects.filter(name__in=skill_names).values_list("id", flat=True)
        )  # Fetch IDs

    def create_job(self):
        """Helper method to create a job"""
        employer = self.create_employer_profile()
        job = Jobs.objects.create(
            employer=employer,
            job_title="Software Engineer",
            description="We are looking for a skilled software engineer to join our team. The ideal candidate will be proficient in Python, Django, and web development.",
            location="New York, NY",
            salary_min=70000,
            salary_max=120000,
            job_type="FT",
            experience_level="mid",
            posted_date="2024-11-14",
            is_active=True,
        )
        ids = self.create_skills()
        job.required_skills.set(ids)
        job.save()
        return job

    def test_get_job_details_success(self):
        """Test retrieving job details successfully"""

        response = self.client.get(self.job_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Jobs Details retrieved successfully", response.data["message"])
        self.assertEqual(response.data["data"]["id"], self.job.id)

    def test_get_job_details_not_found(self):
        """Test retrieving job details when the job does not exist"""

        non_existing_job_url = f"http://127.0.0.1:8000/api/jobs/job/9999999/"
        response = self.client.get(non_existing_job_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Job not found", response.data["message"])

    def test_get_job_details_without_employer_profile(self):
        """Test retrieving job details without an employer profile"""

        # Simulate a user without an employer profile
        self.create_user(type="applicant")
        response = self.client.get(self.job_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("jobs.models.EmployerProfile.objects.get")
    def test_internal_server_error_job_get(self, mock_get_employer):
        """Test unexpected exception handling"""
        # Simulate an unexpected error during the request
        mock_get_employer.side_effect = Exception("Something went wrong.")

        response = self.client.get(self.job_url)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ===========================PUT=============================
    def test_update_job_success(self):
        """Test updating a job successfully"""

        update_data = {
            "job_title": "Updated Job Title",
            "description": "Updated job description",
        }

        response = self.client.put(self.job_url, data=update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_job_not_found(self):
        """Test updating a job that doesn't exist"""

        non_existing_job_url = f"http://127.0.0.1:8000/api/jobs/job/9999999/"
        update_data = {"job_type": "Updated Job Title"}
        response = self.client.put(non_existing_job_url, data=update_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_job_without_employer_profile(self):
        """Test updating a job without an employer profile"""

        # Simulate a user without an employer profile
        self.create_user(type="applicant")
        update_data = {"job_type": "Updated Job Title"}
        response = self.client.put(self.job_url, data=update_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_job_with_invalid_data(self):
        """Test updating a job with invalid data"""

        update_data = {
            "job_type": 1,
            "description": "Updated job description",
        }

        response = self.client.put(self.job_url, data=update_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("jobs.models.EmployerProfile.objects.get")
    def test_internal_server_error_job_update(self, mock_get_employer):
        """Test unexpected exception handling"""
        # Simulate an unexpected error during the request
        mock_get_employer.side_effect = Exception("Something went wrong.")

        update_data = {
            "job_type": "Updated Job Title",
            "description": "Updated job description",
        }

        response = self.client.put(self.job_url, data=update_data)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ======================Delete======================================

    def test_delete_job_success(self):
        """Test deleting a job successfully"""

        response = self.client.delete(self.job_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_job_not_found(self):
        """Test deleting a job that doesn't exist"""

        non_existing_job_url = f"http://127.0.0.1:8000/api/jobs/job/9999999/"
        response = self.client.delete(non_existing_job_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_job_without_employer_profile(self):
        """Test deleting a job without an employer profile"""

        # Simulate a user without an employer profile
        self.create_user(type="applicant")
        response = self.client.delete(self.job_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("jobs.models.EmployerProfile.objects.get")
    def test_internal_server_error_job_delete(self, mock_get_employer):
        """Test unexpected exception handling"""
        # Simulate an unexpected error during the request
        mock_get_employer.side_effect = Exception("Something went wrong.")

        response = self.client.delete(self.job_url)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    # =========================EmployerJob================================
    def test_retrieve_employer_jobs_success(self):
        """Test retrieving jobs for an employer"""
        employer = self.create_employer_profile()
        self.job = self.create_job()
        response = self.client.get(self.employer_job)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_jobs_no_employer_profile(self):
        """Test retrieval fails if employer profile does not exist"""
        self.create_user(type="employer")  # Create user without a profile

        response = self.client.get(self.employer_job)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_jobs_empty_list(self):
        """Test retrieving jobs when no jobs exist for the employer"""
        employer = (
            self.create_employer_profile()
        )  # Create employer profile, but no jobs

        response = self.client.get(self.employer_job)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("jobs.models.EmployerProfile.objects.get")
    def test_internal_server_error_employer_job_get(self, mock_get_employer):
        """Test unexpected exception handling"""
        # Simulate an unexpected error during the request
        mock_get_employer.side_effect = Exception("Something went wrong.")

        response = self.client.get(self.employer_job)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ===========================JobApplication=============================
    def test_create_job_application_success(self):
        """Test creating a job application successfully"""
        applicant = self.create_applicant_profile()  # Uses the fixed method
        job_application_data = {
            "job_listing": self.job.id,
            "applicant": applicant.id,
        }

        response = self.client.post(self.job_application, data=job_application_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_job_application_invalid_data(self):
        """Test creating a job application with invalid data"""
        applicant = self.create_applicant_profile()
        job = self.create_job()
        data = {"applicant": applicant.id, "job_listing": 3333242}
        response = self.client.post(self.job_application, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_job_application_unauthenticated(self):
        """Test creating a job application without authentication"""
        self.client.credentials()  # Remove authentication
        response = self.client.post(self.job_application, data={})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def create_job_application(self, applicant=None):
        """Helper method to create a job application"""
        if not applicant:
            applicant = self.create_applicant_profile()
        job = self.create_job()
        new_job = JobApplication.objects.create(applicant=applicant, job_listing=job)
        new_job.save()
        return new_job

    @patch("jobs.models.JobApplication.save")
    def test_internal_server_error_job_application_create(self, mock_get_employer):
        """Test unexpected exception handling"""
        # Simulate an unexpected error during the request
        mock_get_employer.side_effect = Exception("Something went wrong.")

        applicant = self.create_applicant_profile()  # Uses the fixed method
        job_application_data = {
            "job_listing": self.job.id,
            "applicant": applicant.id,
        }

        response = self.client.post(self.job_application, data=job_application_data)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ==================================GET==========================================

    def test_get_job_applications_success(self):
        """Test retrieving job applications successfully"""
        self.test_create_job_application_success()
        response = self.client.get(self.job_application)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_job_applications_no_applicant_profile(self):
        """Test retrieving job applications when no applicant profile exists"""
        self.create_user(type="employer")  # Create a user without an applicant profile
        response = self.client.get(self.job_application)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_job_applications_unauthenticated(self):
        """Test retrieving job applications without authentication"""
        self.client.credentials()  # Remove authentication
        response = self.client.get(self.job_application)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("jobs.models.JobApplication.objects.filter")
    def test_internal_server_error_job_application_get(self, mock_get_job_application):
        """Test unexpected exception handling in job application retrieval"""
        # Simulate an unexpected error during the request
        mock_get_job_application.side_effect = Exception("Something went wrong.")

        # Ensure a job application exists
        self.test_create_job_application_success()  # Assuming you have a helper to create this

        response = self.client.get(self.job_application)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("errors", response.data)

    # ====================Delete=====================================
    def test_delete_job_application_success(self):
        """Test deleting a job application successfully"""
        self.test_create_job_application_success()
        job_application_response = self.client.get(self.job_application)
        response = self.client.delete(
            f"{self.job_application}{job_application_response.data.get('data')[0].get('id')}/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_job_application_not_found(self):
        """Test deleting a job application that does not exist"""
        response = self.client.delete(f"{self.job_application}999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_job_application_unauthenticated(self):
        """Test deleting a job application without authentication"""
        job_application = self.create_job_application()
        self.client.credentials()  # Remove authentication
        response = self.client.delete(f"{self.job_application}{job_application.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("jobs.models.JobApplication.objects.get")
    def test_internal_server_error_job_application_delete(self, mock_get_employer):
        """Test unexpected exception handling"""
        # Simulate an unexpected error during the request
        mock_get_employer.side_effect = Exception("Something went wrong.")
        self.test_create_job_application_success()
        job_application_response = self.client.get(self.job_application)
        response = self.client.delete(
            f"{self.job_application}{job_application_response.data.get('data')[0].get('id')}/"
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
