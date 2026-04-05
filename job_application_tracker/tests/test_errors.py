import unittest
from unittest.mock import patch

from django.urls import reverse

from core.test import TestCase
from core.tests.mixins import BaseAuthenticatedUserMixin


class TestErrors(BaseAuthenticatedUserMixin, TestCase):
    """
    This class is intended to hold the tests for the various error pages (400, 403, 404 and 500), as I find out how
    to get Django to exhibit those errors, and others I might come across, as I will eventually have middleware
    logging many of those errors.
    """

    def test_400_error_gets_expected_page(self):
        # Arrange
        test_url = reverse("home")

        # Act
        results = self.client.get(test_url, HTTP_HOST="bogus.example.com")

        # Assert
        self.assertEqual(results.status_code, 400)
        self.assertTemplateUsed("400.html")

    def test_403_error_on_csrf_gets_expected_page(self):
        # Arrange
        client = self.client_class(enforce_csrf_checks=True)
        client.force_login(self.test_user_1)
        test_url = reverse("password_change")
        data = {
            "old_password": "testuser1",
            "new_password1": "Yfr_A0Qdk7W-s2s01Mec ",
            "new_password2": "Yfr_A0Qdk7W-s2s01Mec ",
        }

        # Act
        response = client.post(test_url, data)

        # Assert
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed("403.html")

    def test_404_error_gets_expected_page(self):
        # Arrange
        test_url = "/some/bogus/url"

        # Act
        response = self.client.get(test_url)

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed("404.html")

    # Need to investigate why the patch does not work for this test. I have tried all the combinations, and only this
    # one does not get an error from the patching attempt, but instead allows the original code to execute, contrary
    # to what we want.
    @patch("job_application_tracker.urls.views.about")
    def no_test_500_error_gets_expected_page(self, mocked_about):
        # Arrange
        test_url = reverse("about")
        mocked_about.side_effect = Exception("Simulated production failure")

        # Act
        response = self.client.get(test_url)

        # Assert
        self.assertEqual(response.status_code, 500)
        self.assertTemplateUsed("500.html")


if __name__ == "__main__":
    unittest.main()
