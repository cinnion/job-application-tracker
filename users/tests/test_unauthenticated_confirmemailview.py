"""
Our class based tests for dealing with unauthenticated users trying to do
actions related to a user confirming their email.
"""
import time
import unittest

from allauth.account import app_settings
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.contrib.messages import (
    Message,
    constants as messages
)
from django.contrib.messages.test import MessagesTestMixin
from django.contrib.sessions.serializers import JSONSerializer
from django.core import signing
from django.urls import reverse

from core.test import TestCase


class MyTimestampSigner(signing.TimestampSigner):
    """
    This class extends django.core.signing.TimestampSigner, and is used to generate the key
    for testing, using an optionally injected timestamp.
    """
    my_timestamp: int | None = None

    def __init__(self, *, key=None, sep=":", salt=None, fallback_keys=None, timestamp: int | None = None):
        """
        Initialize our class.

        Args:
            key: The key to sign.
            sep: The separator.
            salt: The salt to use.
            fallback_keys: The fallback keys.
            timestamp: The timestamp.
        """
        super().__init__(key=key, sep=sep, salt=salt, fallback_keys=fallback_keys)

        if timestamp:
            self.my_timestamp = int(timestamp)

    def timestamp(self) -> str:
        """
        Get our timestamp, which could have been optionally specified, in base-62 encoded format.

        Returns: The timestamp in base-62 encoded format.
        """
        if self.my_timestamp is None:
            self.my_timestamp = int(time.time())

        return signing.b62_encode(self.my_timestamp)


# noinspection DuplicatedCode - These tests are near duplicates of one another, but test different endpoints.
class TestUnauthenticatedConfirmEmailView(MessagesTestMixin, TestCase):
    """
    Test the authentication of the email using a token embedded into a URL sent via email.

    The fixture is needed so that we have our groups for testing purposes, but
    it results in a base count of 4 users and email records before any test
    creates a user.
    """
    fixtures = ["core/tests/fixtures/users.json"]

    def getSignatureKey(self, timestamp: int | None = None) -> str:
        """
        Generate a signature key like those used to verify a user's email address.

        Args:
            timestamp: The desired timestamp for the key, or None to use the current time.

        Returns: The string which is used as a signature key.
        """
        return MyTimestampSigner(key=None, salt=app_settings.SALT, timestamp=timestamp).sign_object(
            self.email_address.pk, serializer=JSONSerializer, compress=False
        )

    def getConfirmationLink(self, timestamp: int | None = None) -> str:
        """
        Get the confirmation link which would be sent in an email.

        Args:
            timestamp: The desired timestamp for the key, or None to use the current time.

        Returns: The URL to use.
        """
        key = self.getSignatureKey(timestamp=timestamp)
        return reverse("account_confirm_email", kwargs={"key": key})

    def setUp(self):
        """
        Create a test user who is in the process of authenticating the account via email.

        Returns: None
        """
        # Arrange
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "email2": "testuser@example.com",
            "password1": "Yfr_A0Qdk7W-s2s01Mec ",
            "password2": "Yfr_A0Qdk7W-s2s01Mec ",
        }

        # Act
        response = self.client.post(reverse("account_signup"), data)

        # Assert
        self.assertRedirects(response, reverse("account_email_verification_sent"))
        self.user = get_user_model().objects.get(username=data["username"])
        self.email_address = EmailAddress.objects.filter(user=self.user).first()
        self.password = data["password1"]

    def test_get_with_invalid_token_results_in_unenumerated_error_response(self):
        # Arrange
        url = reverse("account_confirm_email", kwargs={"key": "NQ:1wH9Ww:SjMSD-vfyAZvl_03T5a9iIV0v9-S3FfvVTJSu34mku1"})
        response_url = reverse("account_email")

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "master.html")
        self.assertTemplateUsed(response, "user-master.html")
        self.assertTemplateUsed(response, f"account/email_confirm.{app_settings.TEMPLATE_EXTENSION}")
        self.assertContains(response,
                            f"This email confirmation link expired or is invalid. Please <a href=\"{response_url}\">"
                            "issue a new email confirmation request</a>.")

    def test_get_with_expired_token_results_in_unenumerated_error_response(self):
        # Arrange
        timestamp = int(time.time()) - 60 * 60 * 24 * 30
        url = self.getConfirmationLink(timestamp=timestamp)
        response_url = reverse("account_email")

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "master.html")
        self.assertTemplateUsed(response, "user-master.html")
        self.assertTemplateUsed(response, f"account/email_confirm.{app_settings.TEMPLATE_EXTENSION}")
        self.assertContains(response,
                            f"This email confirmation link expired or is invalid. Please <a href=\"{response_url}\">"
                            "issue a new email confirmation request</a>.")

    def test_get_with_current_token_results_in_response_with_confirm_form(self):
        # Arrange
        key = self.getSignatureKey()
        url = reverse("account_confirm_email", kwargs={"key": key})

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "master.html")
        self.assertTemplateUsed(response, "user-master.html")
        self.assertTemplateUsed(response, f"account/email_confirm.{app_settings.TEMPLATE_EXTENSION}")
        self.assertContains(response,
                            "Please confirm that <a href=\"mailto:testuser@example.com\">testuser@example.com</a>"
                            " is an email address for user testuser."
                            )
        self.assertContains(response, f"action=\"{url}\"")
        self.assertContains(response, "method=\"post\"")

    def test_post_with_expired_token_results_in_redirect_to_404_error(self):
        # Arrange
        timestamp = int(time.time()) - 60 * 60 * 24 * 30
        key = self.getSignatureKey(timestamp=timestamp)
        url = reverse("account_confirm_email", kwargs={"key": key})

        # Act
        response = self.client.post(url, follow=True)

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "master.html")
        self.assertTemplateUsed(response, "404.html")

    def test_post_with_current_token_results_in_redirect_to_login(self):
        # Arrange
        key = self.getSignatureKey()
        url = reverse("account_confirm_email", kwargs={"key": key})

        # Act
        response = self.client.post(url, follow=True)

        # Assert
        self.assertRedirects(response, reverse("account_login"))
        self.assertTemplateUsed(response, "master.html")
        self.assertTemplateUsed(response, "user-master.html")
        self.assertTemplateUsed(response, f"account/login.{app_settings.TEMPLATE_EXTENSION}")
        self.assertMessages(response, [Message(messages.SUCCESS, "You have confirmed testuser@example.com.")])

    def test_put_request_gets_an_error(self):
        # Arrange
        key = self.getSignatureKey()
        url = reverse("account_confirm_email", kwargs={"key": key})

        # Act
        response = self.client.put(url)

        # Assert
        self.assertEqual(response.status_code, 405)

    def test_patch_request_gets_an_error(self):
        # Arrange
        key = self.getSignatureKey()
        url = reverse("account_confirm_email", kwargs={"key": key})

        # Act
        response = self.client.patch(url)

        # Assert
        self.assertEqual(response.status_code, 405)

    def test_delete_request_gets_an_error(self):
        # Arrange
        key = self.getSignatureKey()
        url = reverse("account_confirm_email", kwargs={"key": key})

        # Act
        response = self.client.delete(url)

        # Assert
        self.assertEqual(response.status_code, 405)

    def test_head_request_gets_a_200_response(self):
        # Arrange
        key = self.getSignatureKey()
        url = reverse("account_confirm_email", kwargs={"key": key})

        # Act
        response = self.client.head(url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 0)

    def test_options_request_gets_an_error(self):
        # Arrange
        key = self.getSignatureKey()
        url = reverse("account_confirm_email", kwargs={"key": key})

        # Act
        response = self.client.options(url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['allow'], 'GET, POST, HEAD, OPTIONS')


if __name__ == "__main__":
    unittest.main()
