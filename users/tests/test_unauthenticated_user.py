"""
Our class based tests for dealing with unauthenticated users trying to do user profile related
actions.
"""
import unittest
from urllib.parse import urlencode

from django.conf import settings
from django.urls import reverse

from core.test import TestCase


# noinspection DuplicatedCode - These tests are near duplicates of one another, but test different endpoints.
class TestUnauthenticatedChangePasswordView(TestCase):
    """
    This class tests our extensions to the default user model found in django.contrib.auth.models
    """
    test_url = reverse("password_change")
    login_url = reverse(settings.LOGIN_URL)
    expected_redirect_url = f"{login_url}?{urlencode({'next': test_url})}"

    def test_get_receives_redirect_to_login_with_next(self):
        # Arrange

        # Act
        response = self.client.get(self.test_url)

        # Assert
        self.assertRedirects(
            response,
            self.expected_redirect_url,
            status_code=302,
            target_status_code=200
        )

    def test_post_receives_redirect_to_login_with_next(self):
        # Arrange
        data = {}

        # Act
        response = self.client.post(self.test_url, data)

        # Assert
        self.assertRedirects(
            response,
            self.expected_redirect_url,
            status_code=302,
            target_status_code=200
        )

    def test_put_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.put(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 302)

    def test_patch_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.patch(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 302)

    def test_delete_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.delete(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 302)

    def test_head_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.head(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 302)

    def test_options_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.options(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 302)


# noinspection DuplicatedCode - These tests are near duplicates of one another, but test different endpoints.
class TestUnauthenticatedEditProfileView(TestCase):
    """
    This class tests our extensions to the default user model found in django.contrib.auth.models
    """
    test_url = reverse("profile")
    login_url = reverse(settings.LOGIN_URL)
    expected_redirect_url = f"{login_url}?{urlencode({'next': test_url})}"

    def test_get_receives_redirect_to_login_with_next(self):
        # Arrange

        # Act
        response = self.client.get(self.test_url)

        # Assert
        self.assertRedirects(
            response,
            self.expected_redirect_url,
            status_code=302,
            target_status_code=200
        )

    def test_post_receives_redirect_to_login_with_next(self):
        # Arrange
        data = {}

        # Act
        response = self.client.post(self.test_url, data)

        # Assert
        self.assertRedirects(
            response,
            self.expected_redirect_url,
            status_code=302,
            target_status_code=200
        )

    def test_put_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.put(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 302)

    def test_patch_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.patch(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 302)

    def test_delete_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.delete(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 302)

    def test_head_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.head(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 302)

    def test_options_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.options(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 302)


if __name__ == "__main__":
    unittest.main()
