"""
Test for verifying functionality surrounding an unauthenticated user trying to access
job applications either as a list or individually.
"""
import unittest

from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse


class UnauthenticatedApplicationTests(TestCase):
    """
    Our tests for verifying that unauthenticated users do not get access to job applications,
    and either get redirected to the login page, or get the appropriate error for methods which
    do not exist.
    """

    def setUp(self):
        """
        Create our client for use by the tests.
        """
        self.client = Client()

        self.login_url = reverse(settings.LOGIN_URL)

    def test_unauthenticated_user_gets_redirected_from_applications(self):
        # Arrange
        test_url = reverse("applications:application-list")

        # Act
        response = self.client.get(test_url)

        # Assert
        self.assertRedirects(
            response,
            f"{self.login_url}?next={test_url}",
            status_code=302,
            target_status_code=200
        )

    def test_unauthenticated_user_gets_redirected_from_application_details(self):
        # Arrange
        test_url = reverse("applications:application-details", args=(1,))

        # Act
        response = self.client.get(test_url)

        # Assert
        self.assertRedirects(
            response,
            f"{self.login_url}?next={test_url}",
            status_code=302,
            target_status_code=200
        )

    def test_unauthenticated_user_edit_application_post_gets_redirected(self):
        # Arrange
        data = {
            "when": "1999-12-31",
            "company": "Some company",
            "title": "Some title"
        }
        test_url = reverse("applications:application-details", args=(1,))

        # Act
        response = self.client.post(test_url, data)

        # Assert
        self.assertRedirects(
            response,
            f"{self.login_url}?next={test_url}",
            status_code=302,
            target_status_code=200
        )

    def test_unauthenticated_user_gets_redirected_from_new_application(self):
        # Arrange
        test_url = reverse("applications:new-application")

        # Act
        response = self.client.get(test_url)

        # Assert
        self.assertRedirects(
            response,
            f"{self.login_url}?next={test_url}",
            status_code=302,
            target_status_code=200
        )

    def test_unauthenticated_user_post_gets_redirected_from_new_application(self):
        # Arrange
        data = {
            "when": "1999-12-31",
            "company": "Some company",
            "title": "Some title"
        }
        test_url = reverse("applications:new-application")

        # Act
        response = self.client.post(test_url, data)

        # Assert
        self.assertRedirects(
            response,
            f"{self.login_url}?next={test_url}",
            status_code=302,
            target_status_code=200
        )


if __name__ == "__main__":
    unittest.main()
