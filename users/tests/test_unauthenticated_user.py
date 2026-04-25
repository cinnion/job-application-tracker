"""
Our class based tests for dealing with unauthenticated users trying to do user profile related
actions.
"""
import unittest
from urllib.parse import urlencode

from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.messages import (
    Message,
    constants as messages,
)
from django.contrib.messages.test import MessagesTestMixin
from django.core import mail
from django.urls import reverse

from core.test import TestCase


class TestUnauthenticatedLoginView(MessagesTestMixin, TestCase):
    """
    This class tests our login view.
    """
    login_url = reverse(settings.LOGIN_URL)

    def test_get_receives_login_view(self):
        # Arrange

        # Act
        response = self.client.get(self.login_url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "master.html")
        self.assertTemplateUsed(response, "user-master.html")
        self.assertTemplateUsed(response, "registration/login.html")
        form = response.context_data["form"]
        self.assertEqual(form.fields['login'].label, "Username")
        self.assertEqual(form.fields['password'].label, "Password")

    def test_post_unverified_user_with_correct_credentials_gets_verification_page(self):
        # Arrange
        client = self.client_class()
        username = "testuser1"
        password = "Test user1 "
        email = "test@example.com"
        user = get_user_model().objects.create(username=username, email=email)
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
        email = "test@example.com"
        user = get_user_model().objects.create(username=username, email=email)
        user.set_password(password)
        user.save()
        EmailAddress.objects.create(
            user=user,
            email=user.email,
            primary=True,
            verified=True
        )

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


# noinspection DuplicatedCode - These tests are near duplicates of one another, but test different endpoints.
class TestUnauthenticatedChangePasswordView(TestCase):
    """
    This class tests our extensions to the default user model found in django.contrib.auth.models
    """
    test_url = reverse("account_change_password")
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
