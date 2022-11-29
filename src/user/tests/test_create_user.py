from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_API = reverse("create_user")


def create_user(**params):
    """Create and return a new user
    Requires only two arguments
    email and password
    """
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public feature of the user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user in successful"""
        # we added an extra password2 field to the UserSerializer
        # so we need to pass password2 when
        # we are submitting a post request in the "create_user" API

        payload = {
            "email": "test@example.com",
            "password": "testpassword123",
            "password2": "testpassword123",
        }
        # here payload is the content that is posted to the url
        response = self.client.post(CREATE_USER_API, payload)
        # check status code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # validating that the user object is created with the payload credentials
        user = get_user_model().objects.get(email=payload["email"])
        # check_password checks the password of the user
        # with the plain text format
        self.assertTrue(user.check_password(payload["password"]))
        # checking that the user password is not available in the response
        # we are checking that there is no key named "password" in the returned response from the API
        self.assertNotIn("password", response.data)


    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        payload1 = {
            "email": "test@example.com",
            "password": "testpassword123",
            # "password2": "testpassword123",
        }
        payload2 = {
            "email": "test@example.com",
            "password": "testpassword123",
            "password2": "testpassword123",
        }
        # here using **payload is equivalent to
        # email=test@example.com, password=testpassword123
        create_user(**payload1)
        response = self.client.post(CREATE_USER_API, payload2)
        print(f"response data -->{response.data}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)