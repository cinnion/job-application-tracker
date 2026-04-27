"""
Our class based tests for dealing with unauthenticated users trying to do user
login actions.
"""
import unittest

from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.messages import (
    Message,
    constants as messages,
)
from django.contrib.messages.test import MessagesTestMixin
from django.core import mail
from django.core.cache import cache
from django.urls import reverse

from core.test import TestCase


class TestUnauthenticatedLoginView(MessagesTestMixin, TestCase):
    """
    This class tests our login view.

    The fixture is needed so that we have our groups for testing purposes, but
    it results in a base count of 4 users and email records before any test
    creates a user.
    """
    login_url = reverse(settings.LOGIN_URL)
    fixtures = ["core/tests/fixtures/users.json"]

    def setUp(self) -> None:
        """
        Clear our cache.
        Returns: None
        """
        cache.clear()

    def test_get_receives_login_view(self):
        # Arrange

        # Act
        response = self.client.get(self.login_url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "master.html")
        self.assertTemplateUsed(response, "user-master.html")
        self.assertTemplateUsed(response, "account/login.html")
        form = response.context_data["form"]
        self.assertEqual(form.fields["login"].label, "Username")
        self.assertEqual(form.fields["password"].label, "Password")

    def test_post_unverified_user_with_correct_credentials_gets_verification_page(self):
        # Arrange
        client = self.client_class()
        username = "testuser1"
        password = "Test user1 "
        user = get_user_model().objects.get(username=username)
        user.set_password(password)
        user.save()
        email_record = EmailAddress.objects.filter(user=user).first()
        email_record.verified = False
        email_record.save()

        data = {
            "login": user.username,
            "password": password
        }

        # Act
        response = client.post(self.login_url, data)

        # Assert
        self.assertRedirects(response,
                             reverse("account_email_verification_sent"),
                             )
        self.assertMessages(response, [Message(messages.INFO, f"Confirmation email sent to {user.email}.")])
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "[testserver] Please Confirm Your Email Address")
        self.assertEqual(mail.outbox[0].to, [user.email])

    def test_post_verified_user_with_correct_credentials_gets_redirect_with_message(self):
        # Arrange
        client = self.client_class()
        username = "testuser1"
        password = "Test user1 "
        user = get_user_model().objects.get(username=username)
        user.set_password(password)
        user.save()

        data = {
            "login": user.username,
            "password": password
        }

        # Act
        response = client.post(self.login_url, data)

        # Assert
        self.assertRedirects(response,
                             reverse(settings.LOGIN_REDIRECT_URL),
                             )
        self.assertMessages(response, [Message(messages.SUCCESS, f"Successfully signed in as {user.username}.")])


if __name__ == "__main__":
    unittest.main()
