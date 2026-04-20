"""
The tests for the DRF API for job applications involving unauthenticated users.
"""
import unittest

from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase


# noinspection DuplicatedCode - These tests are near duplicates of one another, but test different endpoints.
class UnauthenticatedApplicationTests(APITestCase):
    """
    The unauthenticated user tests for the DRF API for job applications.
    """

    def setUp(self):
        """
        Create our client for use by the tests.
        """
        self.client = self.client_class()

        self.login_url = reverse(settings.LOGIN_URL)

    def test_unauthenticated_user_get_receives_403_forbidden_from_applications_api_list(self):
        # Arrange
        test_url = reverse("applications-api:applications-list")
        expected_response_data = {
            "detail": ErrorDetail(string="Authentication credentials were not provided.", code="not_authenticated")
        }

        # Act
        response = self.client.get(test_url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(response.data, expected_response_data)

    def test_unauthenticated_user_gets_redirected_from_applications_api_details(self):
        # Arrange
        test_url = reverse("applications-api:application-details", kwargs={"pk": 1})
        expected_response_data = {
            "detail": ErrorDetail(string="Authentication credentials were not provided.", code="not_authenticated")
        }

        # Act
        response = self.client.get(test_url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(response.data, expected_response_data)


if __name__ == "__main__":
    unittest.main()
