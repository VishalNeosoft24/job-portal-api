from unittest.mock import patch

from django.urls import reverse
from faker import Faker
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from users.models import Skill

fake = Faker()


class UsersTestSetup(APITestCase):
    def setUp(self):
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.applicant_profile_url = reverse("applicant_profile")
        self.token_url = reverse("token_obtain_pair")
        self.access_token = ""
        self.logout_url = reverse("logout")
        self.refresh_token = ""

        user_common_data = {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "username": fake.user_name(),
            "password": fake.password(),
            "email": fake.email(),
        }

        self.applicant_user_data = {
            **user_common_data,
            "user_type": "Applicant",
        }

        self.employer_user_data = {
            **user_common_data,
            "user_type": "Employer",
        }

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

        # Register the user and get the access token
        self.create_and_authenticate_user()
        return super().setUp()

    def create_and_authenticate_user(self):
        """Helper method to create a user and authenticate them"""
        response = self.client.post(self.register_url, data=self.applicant_user_data)
        self.assertEqual(response.status_code, 201)

        # Obtain access token
        token_res = self.client.post(
            self.token_url,
            data={
                "username": self.applicant_user_data["username"],
                "password": self.applicant_user_data["password"],
            },
        )
        self.assertEqual(token_res.status_code, status.HTTP_200_OK)
        self.access_token = token_res.data["access"]
        self.refresh_token = token_res.data["refresh"]

        #  set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def assert_error_response(self, response):
        self.assertEqual(
            response.status_code, 400, "Status code is not 400 for error response."
        )
        # Check for 'status' and 'message' in the response
        self.assertEqual(response.data["status"], "error", "Status key is not 'error'.")
        self.assertIn(
            "message", response.data, "message key is missing in the response."
        )
        self.assertIn("errors", response.data, "Errors key is missing in the response.")

    # ------------- USER TEST CASES -------------

    def test_register_with_valid_data(self, *args, **kwargs):
        """Test registering a new user"""
        user_data_register_only = {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "username": fake.user_name(),
            "password": fake.password(),
            "email": fake.email(),
            "user_type": "Applicant",
        }
        response = self.client.post(self.register_url, data=user_data_register_only)
        self.assertEquals(response.status_code, 201)
        self.client.login(
            username=user_data_register_only["username"],
            password=user_data_register_only["password"],
        )

    def test_register_with_duplicate_username(self):
        """Test registering with a duplicate username"""
        # Attempt to register with the duplicate username
        response = self.client.post(self.register_url, data=self.applicant_user_data)
        self.assertEqual(response.status_code, 400)

    def test_register_with_missing_required_fields(self):
        """Test registering with missing required fields"""
        incomplete_data = self.applicant_user_data.copy()
        incomplete_data.pop("username")
        response = self.client.post(self.register_url, data=incomplete_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("errors", response.data, "Errors key is missing in the response.")

    def test_register_with_invalid_user_type(self):
        """Test registering with an invalid user type"""
        invalid_data = self.applicant_user_data.copy()
        invalid_data["user_type"] = "InvalidType"
        response = self.client.post(self.register_url, data=invalid_data)
        self.assertEqual(response.status_code, 400)

    @patch(
        "api.users.serializers.UserRegisterSerializer.save"
    )  # Mock save method of the serializer
    def test_register_with_unexpected_error(self, mock_save):
        """Test registering a user when an unexpected error occurs"""

        # Simulate an exception being raised during save
        mock_save.side_effect = Exception("Unexpected error")

        user_data_register_only = {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "username": fake.user_name(),
            "password": fake.password(),
            "email": fake.email(),
            "user_type": "Applicant",
        }

        response = self.client.post(self.register_url, data=user_data_register_only)
        # Check that the response status code is 500
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Check the error message in the response
        self.assertEqual(response.data["message"], "An unexpected error occurred.")

        # Check that the error field contains the exception message
        self.assertIn("errors", response.data)
        self.assertEqual(response.data["errors"], "Unexpected error")

    def test_login_user_with_valid_data(self):
        """Test login with valid credentials"""
        # Valid credentials
        response = self.client.post(
            self.login_url,
            data={
                "username": self.applicant_user_data["username"],
                "password": self.applicant_user_data["password"],
            },
        )
        self.assertEqual(
            response.status_code, 200, msg="Login failed with valid credentials"
        )

    def test_login_user_with_missing_data(self):
        """Test login with missing credentials"""

        # Missing credentials
        response = self.client.post(self.login_url, data={})
        self.assertEqual(
            response.status_code, 400, msg="Login succeeded with empty data"
        )

    def test_login_with_invalid_username(self):
        """Login with invalid username and password"""

        response = self.client.post(
            self.login_url,
            data={
                "username": "test_sample",
                "password": "est_sample",
            },
        )
        self.assertEqual(response.status_code, 401)

    def test_logout_with_valid_token(self):
        """Logout with valid token"""

        response = self.client.post(
            self.logout_url, data={"refresh_token": self.refresh_token}
        )
        self.assertEqual(response.status_code, 200)

    @patch(
        "rest_framework_simplejwt.tokens.RefreshToken.blacklist"
    )  # Mock blacklist method of RefreshToken
    def test_logout_with_unexpected_error(self, mock_blacklist):
        """Test logout when an unexpected error occurs (simulating an exception)"""

        # Simulate an exception being raised when attempting to blacklist the token
        mock_blacklist.side_effect = Exception("Unexpected error")

        response = self.client.post(
            self.logout_url, data={"refresh_token": self.refresh_token}
        )

        # Check that the response status code is 500
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Check the error message in the response
        self.assertEqual(response.data["message"], "An unexpected error occurred.")

        # Check that the error field contains the exception message
        self.assertIn("errors", response.data)
        self.assertEqual(response.data["errors"], "Unexpected error")


class ApplicantProfileTestSetup(APITestCase):
    def setUp(self):
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.applicant_profile_url = reverse("applicant_profile")
        self.employer_profile_url = reverse("employer_profile")
        self.token_url = reverse("token_obtain_pair")
        self.access_token = ""
        self.logout_url = reverse("logout")
        self.refresh_token = ""

        user_common_data = {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "username": fake.user_name(),
            "password": fake.password(),
            "email": fake.email(),
        }

        self.applicant_user_data = {
            **user_common_data,
            "user_type": "Applicant",
        }

        self.employer_user_data = {
            **user_common_data,
            "user_type": "Employer",
        }

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
        self.valid_data = {"phone_number": "9999999999"}
        self.invalid_data = {"skills": [9999]}

        # Register the user and get the access token
        self.create_and_authenticate_user()
        return super().setUp()

    def create_and_authenticate_user(self):
        """Helper method to create a user and authenticate them"""
        response = self.client.post(self.register_url, data=self.applicant_user_data)
        self.assertEqual(response.status_code, 201)

        # Obtain access token
        token_res = self.client.post(
            self.token_url,
            data={
                "username": self.applicant_user_data["username"],
                "password": self.applicant_user_data["password"],
            },
        )
        self.assertEqual(token_res.status_code, status.HTTP_200_OK)
        self.access_token = token_res.data["access"]
        self.refresh_token = token_res.data["refresh"]

        #  set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def get_tokens(self):
        """Test login with valid credentials"""
        # Obtain access token
        token_res = self.client.post(
            self.token_url,
            data={
                "username": self.applicant_user_data["username"],
                "password": self.applicant_user_data["password"],
            },
        )
        self.assertEqual(token_res.status_code, status.HTTP_200_OK)
        self.access_token = token_res.data["access"]
        self.refresh_token = token_res.data["refresh"]

        #  set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    # ------------- APPLICANT PROFILE TEST CASES -------------

    def test_applicant_profile_valid(self, *args, **kwargs):
        """applicant profile"""
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

    def test_applicant_profile_with_duplicate_data(self, *args, **kwargs):
        """applicant profile with duplicate data"""
        Skill.objects.bulk_create(
            [Skill(name="python"), Skill(name="django"), Skill(name="drf")]
        )
        applicant_profile_data = self.applicant_profile_data.copy()
        applicant_profile_data["skills"] = [4, 5, 6]
        with open(
            "/home/neosoft/Downloads/Darsh_Modi1731414878-DB Crop.pdf", "rb"
        ) as resume:
            response = self.client.post(
                self.applicant_profile_url,
                data={**applicant_profile_data, "resume_file": resume},
                format="multipart",
            )
            self.assertEquals(response.status_code, 201)
            res = self.client.post(
                self.applicant_profile_url,
                data={**self.applicant_profile_data, "resume_file": resume},
                format="multipart",
            )

        self.assertEquals(res.status_code, 400)

    def test_applicant_profile_missing_required_fields(self):
        """missing required fields"""
        response = self.client.post(
            self.applicant_profile_url,
            data=self.applicant_profile_data,
        )

        self.assertEquals(response.status_code, 400)
        self.assertIn("errors", response.data)

    def test_applicant_profile_invalid_file_type(self):
        """Invalid File type"""
        with open("/home/neosoft/Downloads/test_file.txt", "rb") as invalid_file:
            response = self.client.post(
                self.applicant_profile_url,
                data={**self.applicant_profile_data, "resume_file": invalid_file},
            )

        self.assertEqual(response.status_code, 400)
        self.assertIn("resume_file", response.data["errors"])

    def test_applicant_profile_invalid_skills(self):
        with open(
            "/home/neosoft/Downloads/Darsh_Modi1731414878-DB Crop.pdf", "rb"
        ) as resume:
            # remove skills from applicant_profile data
            self.applicant_profile_data.pop("skills")
            response = self.client.post(
                self.applicant_profile_url,
                data={
                    **self.applicant_profile_data,
                    "resume_file": resume,
                    "skills": [9999],
                },
                format="multipart",
            )
            self.assertEqual(response.status_code, 400)

    def test_applicant_profile_missing_file(self):
        """missing resume file"""

        response = self.client.post(
            self.applicant_profile_url, data=self.applicant_profile_data
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("resume_file", response.data["errors"])

    def test_applicant_profile_empty_fields(self):
        """Applicant Profile Empty Fields"""

        response = self.client.post(
            self.applicant_profile_url,
            data={
                "phone_number": "",
                "address": "",
                "skills": [],
                "profile_complete": True,
            },
        )
        self.assertEquals(response.status_code, 400)

    def test_applicant_profile_large_file(self):
        with open(
            "/home/neosoft/Downloads/Spoken English_ Flourish Your Language.pdf", "rb"
        ) as large_file:
            response = self.client.post(
                self.applicant_profile_url,
                data={**self.applicant_profile_data, "resume_file": large_file},
                format="multipart",
            )
        self.assertIn(response.status_code, [400, 413])  # 413 for Payload Too Large

    def test_applicant_profile_duplicate_submission(self):
        """Applicant Duplicate Profile submission"""
        with open(
            "/home/neosoft/Downloads/Darsh_Modi1731414878-DB Crop.pdf", "rb"
        ) as resume:
            self.client.post(
                self.applicant_profile_url,
                data={**self.applicant_profile_data, "resume_file": resume},
                format="multipart",
            )
            response = self.client.post(
                self.applicant_profile_url,
                data={**self.applicant_profile_data, "resume_file": resume},
                format="multipart",
            )
        self.assertIn(response.status_code, [400, 409])

    def test_get_applicant_profile_with_valid_data(self):
        """Get applicant Profile with valid data"""
        Skill.objects.bulk_create(
            [Skill(name="python"), Skill(name="django"), Skill(name="drf")]
        )
        applicant_profile_data = {
            "phone_number": "1245125412",
            "address": fake.address(),
            "skills": [10, 11, 12],
            "profile_complete": True,
        }
        with open(
            "/home/neosoft/Downloads/Darsh_Modi1731414878-DB Crop.pdf", "rb"
        ) as resume:
            response = self.client.post(
                self.applicant_profile_url,
                data={**applicant_profile_data, "resume_file": resume},
                format="multipart",
            )

            self.assertEquals(response.status_code, 201)

        response = self.client.get(self.applicant_profile_url)
        self.assertEqual(response.status_code, 200)

    def test_applicant_profile_does_not_exist(self):
        """Test retrieving profile when none exists"""
        response = self.client.get(self.applicant_profile_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["message"],
            "An applicant profile does not exist for this user.",
        )

    @patch("users.models.ApplicantProfile.objects.get")
    def test_unexpected_exception(self, mock_get):
        """Test handling of an unexpected exception in ApplicantProfile view"""
        # Force `ApplicantProfile.objects.get` to raise an exception
        mock_get.side_effect = Exception("Unexpected error")

        response = self.client.get(self.applicant_profile_url)
        # Assert the response contains the expected error message and status code
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data["status"], "error")
        self.assertEqual(response.data["message"], "An unexpected error occurred.")
        self.assertIn("Unexpected error", response.data["errors"])

    def test_applicant_profile_without_applicant_profile(self):
        """Applicant Profile without applicant profile"""

        employer_user_data = {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "username": fake.user_name(),
            "password": fake.password(),
            "email": fake.email(),
            "user_type": "Employer",
        }

        response = self.client.post(self.register_url, data=employer_user_data)
        self.assertEqual(response.status_code, 201)
        token_res = self.client.post(
            self.token_url,
            data={
                "username": employer_user_data["username"],
                "password": employer_user_data["password"],
            },
        )
        self.assertEqual(token_res.status_code, status.HTTP_200_OK)
        access_token = token_res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        res = self.client.post(
            self.applicant_profile_url, data=self.applicant_profile_data
        )
        self.assertEqual(res.status_code, 400)

    def test_applicant_profile_unauthorized(self):
        """Unauthorized User"""

        self.client.credentials()  # Remove any tokens
        response = self.client.post(
            self.applicant_profile_url,
            data=self.applicant_profile_data,
        )
        self.assertEquals(response.status_code, 401)

    def test_applicant_profile_expired_token(self):
        """Expired Token"""

        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMxNTY1MzM4LCJpYXQiOjE3MzE1NjQ0MzgsImp0aSI6IjYzZDlhNDhiNDM2NDQxOWNhZmFlYTVmNzE1YmQxMDIxIiwidXNlcl9pZCI6MTB9.zNGhNfb5rRc9cmkp1OOG98ebMLXxGFLOHixwOZDkCxk"
        )
        response = self.client.post(
            self.applicant_profile_url,
            data=self.applicant_profile_data,
        )
        self.assertEquals(response.status_code, 401)

    @patch(
        "api.users.serializers.ApplicantProfileSerializer.save"
    )  # Mock blacklist method of RefreshToken
    def test_applicant_profile_with_unexpected_error(self, mock_blacklist):
        """Test create applicant profile when an unexpected error occurs (simulating an exception)"""

        # Simulate an exception being raised when attempting to blacklist the token
        mock_blacklist.side_effect = Exception("Unexpected error")

        Skill.objects.bulk_create(
            [Skill(name="python"), Skill(name="django"), Skill(name="drf")]
        )
        applicant_profile_data = self.applicant_profile_data.copy()
        applicant_profile_data["skills"] = [7, 8, 9]
        with open(
            "/home/neosoft/Downloads/Darsh_Modi1731414878-DB Crop.pdf", "rb"
        ) as resume:
            response = self.client.post(
                self.applicant_profile_url,
                data={**applicant_profile_data, "resume_file": resume},
                format="multipart",
            )
        # Check that the response status code is 500
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Check the error message in the response
        self.assertEqual(response.data["message"], "An unexpected error occurred.")

        # Check that the error field contains the exception message
        self.assertIn("errors", response.data)
        self.assertEqual(response.data["errors"], "Unexpected error")

    def test_update_applicant_profile_success(self):
        """Test successfully updating an applicant profile"""
        Skill.objects.bulk_create(
            [Skill(name="python"), Skill(name="django"), Skill(name="drf")]
        )
        applicant_profile_data = {
            "phone_number": "1245125412",
            "address": fake.address(),
            "skills": [13, 14, 15],
            "profile_complete": True,
        }
        with open(
            "/home/neosoft/Downloads/Darsh_Modi1731414878-DB Crop.pdf", "rb"
        ) as resume:
            response = self.client.post(
                self.applicant_profile_url,
                data={**applicant_profile_data, "resume_file": resume},
                format="multipart",
            )

            self.assertEquals(response.status_code, 201)
        response = self.client.put(self.applicant_profile_url, data=self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(
            response.data["message"], "Applicant Profile Updated Successfully!"
        )

    def test_update_profile_invalid_data(self):
        """Test updating a profile with invalid data"""
        Skill.objects.bulk_create(
            [Skill(name="python"), Skill(name="django"), Skill(name="drf")]
        )
        applicant_profile_data = {
            "phone_number": "1245125412",
            "address": fake.address(),
            "skills": [16, 17, 18],
            "profile_complete": True,
        }
        with open(
            "/home/neosoft/Downloads/Darsh_Modi1731414878-DB Crop.pdf", "rb"
        ) as resume:
            response = self.client.post(
                self.applicant_profile_url,
                data={**applicant_profile_data, "resume_file": resume},
                format="multipart",
            )

            self.assertEquals(response.status_code, 201)
        response = self.client.put(self.applicant_profile_url, data=self.invalid_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["status"], "error")

    @patch("users.models.ApplicantProfile.objects.get")
    def test_unexpected_exception_in_update(self, mock_get):
        """Test handling of an unexpected exception during profile update"""
        # Force `ApplicantProfile.objects.get` to raise an exception
        mock_get.side_effect = Exception("Unexpected error")

        response = self.client.put(self.applicant_profile_url, data=self.valid_data)

        # Assert the response contains the expected error message and status code
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data["status"], "error")
        self.assertEqual(response.data["message"], "An unexpected error occurred.")
        self.assertIn("Unexpected error", response.data["errors"])

    def test_applicant_profile_does_not_exist_in_update(self):
        """Test retrieving profile when none exists in Update"""
        response = self.client.put(self.applicant_profile_url, data=self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(
            response.data["message"],
            "An applicant profile does not exist for this user.",
        )

    def tearDown(self):
        return super().tearDown()


class EmployerProfileTestSetup(APITestCase):
    def setUp(self):
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.applicant_profile_url = reverse("applicant_profile")
        self.employer_profile_url = reverse("employer_profile")
        self.token_url = reverse("token_obtain_pair")
        self.access_token = ""
        self.logout_url = reverse("logout")
        self.refresh_token = ""

        user_common_data = {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "username": fake.user_name(),
            "password": fake.password(),
            "email": fake.email(),
        }

        self.employer_user_data = {
            **user_common_data,
            "user_type": "Employer",
        }

        self.employer_profile_data = {
            "company_name": fake.company(),
            "company_website": fake.url(),
            "location": fake.city(),
            "description": fake.address(),
        }
        self.update_employer_profile_data = {
            "company_name": "Updated Company Name",
            "company_website": "http://updatedwebsite.com",
        }
        self.valid_data = {"phone_number": "9999999999"}
        self.invalid_data = {"skills": [9999]}

    def create_employer_profile(self):
        """Function to create a employer profile"""
        response = self.client.post(self.register_url, data=self.employer_user_data)
        self.assertEqual(response.status_code, 201)

        # Obtain access token
        token_res = self.client.post(
            self.token_url,
            data={
                "username": self.employer_user_data["username"],
                "password": self.employer_user_data["password"],
            },
        )
        self.assertEqual(token_res.status_code, status.HTTP_200_OK)
        self.access_token = token_res.data["access"]
        self.refresh_token = token_res.data["refresh"]

        #  set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_create_employer_profile_success(self):
        """Test successfully creating an employer profile"""
        self.create_employer_profile()

        # Create employer profile
        response = self.client.post(
            self.employer_profile_url, data=self.employer_profile_data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(
            response.data["message"], "Employer Profile Created Successfully!"
        )

    def test_create_duplicate_employer_profile(self):
        """Test creating a duplicate employer profile"""
        self.create_employer_profile()

        # Create the employer profile for the first time
        self.client.post(self.employer_profile_url, data=self.employer_profile_data)

        # Attempt to create the employer profile again (should fail)
        response = self.client.post(
            self.employer_profile_url, data=self.employer_profile_data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "error")

    def test_create_employer_profile_for_non_employer_user(self):
        """Test creating an employer profile for a user who is not an employer"""
        # Create a regular user (non-employer)
        non_employer_user_data = {
            **self.employer_user_data,
            "user_type": "Applicant",  # Change to a non-employer
        }
        response = self.client.post(self.register_url, data=non_employer_user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Obtain access token
        token_res = self.client.post(
            self.token_url,
            data={
                "username": non_employer_user_data["username"],
                "password": non_employer_user_data["password"],
            },
        )
        self.assertEqual(token_res.status_code, status.HTTP_200_OK)
        access_token = token_res.data["access"]

        # Set authorization header for the non-employer user
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # Attempt to create the employer profile (should fail)
        response = self.client.post(
            self.employer_profile_url, data=self.employer_profile_data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "error")
        self.assertEqual(
            response.data["message"], "This action requires an employer profile."
        )

    def test_create_employer_profile_missing_required_fields(self):
        """Test creating an employer profile with missing required fields"""
        self.create_employer_profile()

        # Provide incomplete data for the employer profile
        incomplete_data = {
            "company_name": fake.company(),  # Missing other fields
        }

        # Attempt to create the employer profile
        response = self.client.post(self.employer_profile_url, data=incomplete_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "company_website", response.data["errors"]
        )  # Assuming company_website is required
        self.assertIn(
            "location", response.data["errors"]
        )  # Assuming location is required

    def test_create_employer_profile_with_invalid_data(self):
        """Test creating an employer profile with invalid data"""
        self.create_employer_profile()

        # Provide invalid data
        invalid_data = {
            "company_name": fake.company(),
            "company_website": "invalid_url",  # Invalid URL format
            "location": fake.city(),
            "description": fake.address(),
        }

        # Attempt to create the employer profile
        response = self.client.post(self.employer_profile_url, data=invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "company_website", response.data["errors"]
        )  # Assuming URL validation fails

    @patch("users.models.EmployerProfile.objects.filter")
    def test_create_employer_profile_unexpected_error(self, mock_filter):
        """Test for an unexpected error when creating an employer profile"""

        # Mock an unexpected error during the profile query
        mock_filter.side_effect = Exception("Unexpected error occurred.")

        self.create_employer_profile()

        # Simulate an unexpected error
        response = self.client.post(
            self.employer_profile_url, data=self.employer_profile_data
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["status"], "error")

    # ----------------GET--------------------------------

    def test_get_employer_profile_success(self):
        """Test successfully retrieving an employer profile"""
        self.create_employer_profile()

        # Create the employer profile
        self.client.post(self.employer_profile_url, data=self.employer_profile_data)

        # Retrieve employer profile
        response = self.client.get(self.employer_profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(
            response.data["message"], "Employer profile retrieved successfully."
        )
        self.assertIn(
            "company_name", response.data["data"]
        )  # Verify that the serialized data contains the company_name

    def test_get_employer_profile_not_found(self):
        """Test when the employer profile does not exist"""
        self.create_employer_profile()

        # Attempt to retrieve the employer profile when it doesn't exist
        response = self.client.get(self.employer_profile_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["status"], "error")
        self.assertEqual(
            response.data["message"],
            "An Employer profile does not exist for this user.",
        )

    @patch("users.models.EmployerProfile.objects.get")
    def test_get_employer_profile_unexpected_error(self, mock_get):
        """Test for an unexpected error during profile retrieval"""
        mock_get.side_effect = Exception("Unexpected error occurred.")

        self.create_employer_profile()

        # Simulate an unexpected error
        response = self.client.get(self.employer_profile_url)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["status"], "error")
        self.assertEqual(response.data["message"], "An unexpected error occurred.")
        self.assertEqual(response.data["errors"], "Unexpected error occurred.")

    # ----------------PUT--------------------------------

    def test_update_employer_profile_success(self):
        """Test successfully updating an employer profile"""
        self.create_employer_profile()

        # Create the employer profile
        self.client.post(self.employer_profile_url, data=self.employer_profile_data)

        # Update employer profile
        response = self.client.put(
            self.employer_profile_url, data=self.update_employer_profile_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(
            response.data["message"], "Employer Profile Updated Successfully!"
        )

    def test_update_employer_profile_not_found(self):
        """Test when the employer profile does not exist"""
        self.create_employer_profile()

        # Attempt to update the employer profile when it doesn't exist
        response = self.client.put(
            self.employer_profile_url, data=self.update_employer_profile_data
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["status"], "error")
        self.assertEqual(
            response.data["message"],
            "An Employer profile does not exist for this user.",
        )

    def test_update_employer_profile_invalid_data(self):
        """Test updating the employer profile with invalid data"""
        self.create_employer_profile()

        # Create the employer profile
        self.client.post(self.employer_profile_url, data=self.employer_profile_data)

        # Update with invalid data (e.g., missing required fields)
        invalid_data = {"company_name": ""}
        response = self.client.put(self.employer_profile_url, data=invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "error")
        self.assertIn("company_name", response.data["errors"])

    @patch("users.models.EmployerProfile.objects.get")
    def test_update_employer_profile_unexpected_error(self, mock_filter):
        """Test for an unexpected error during profile update"""
        mock_filter.side_effect = Exception("Unexpected error occurred.")

        self.create_employer_profile()

        # Simulate an unexpected error
        response = self.client.put(
            self.employer_profile_url, data=self.update_employer_profile_data
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["status"], "error")
