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


class TestUnauthenticatedSignupView(MessagesTestMixin, TestCase):
    """
    Test the SignupView as an unauthenticated user.
    """
    signup_url = reverse("account_signup")
    redirect_url = reverse("account_email_verification_sent")

    def test_get_gets_form_with_correct_templates_and_fields_including_honeypot(self):
        # Arrange

        # Act
        response = self.client.get(self.signup_url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "master.html")
        self.assertTemplateUsed(response, "user-master.html")
        self.assertTemplateUsed(response, "account/signup.html")
        form = response.context_data["form"]
        self.assertEqual(len(form.fields), 6)
        self.assertEqual(form.fields["username"].label, "Username")
        self.assertEqual(form.fields["email"].label, "Email")
        self.assertEqual(form.fields["email2"].label, "Email (again)")
        self.assertEqual(form.fields["password1"].label, "Password")
        self.assertEqual(form.fields["password2"].label, "Password (again)")
        honeypot_attrs = form.fields["phone_number"].widget.attrs
        self.assertEqual(honeypot_attrs["style"], "position: absolute; right: -99999px;")
        self.assertEqual(honeypot_attrs["tabindex"], "-1")

    def test_post_with_email_mismatch_does_not_create_account_or_send_email_but_reports_errors(self):
        # Arrange
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "email2": "testuser2@example.com",
            "password1": "Yfr_A0Qdk7W-s2s01Mec ",
            "password2": "Yfr_A0Qdk7W-s2s01Mec ",
        }

        # Act
        response = self.client.post(self.signup_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/signup.html")
        self.assertMessages(response, [])
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors["email2"]), 1)
        self.assertFormError(
            form,
            "email2",
            "You must type the same email each time."
        )
        self.assertEqual(get_user_model().objects.count(), 0)
        self.assertEqual(EmailAddress.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_post_with_password_mismatch_does_not_create_account_or_send_email_but_reports_errors(self):
        # Arrange
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "email2": "testuser@example.com",
            "password1": "Yfr_A0Qdk7W-s2s01Mec1",
            "password2": "Yfr_A0Qdk7W-s2s01Mec ",
        }

        # Act
        response = self.client.post(self.signup_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/signup.html")
        self.assertMessages(response, [])
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors["password2"]), 1)
        self.assertFormError(
            form,
            "password2",
            "You must type the same password each time."
        )
        self.assertEqual(get_user_model().objects.count(), 0)
        self.assertEqual(EmailAddress.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_post_with_similar_password_does_not_create_account_or_send_email_but_reports_errors(self):
        # Arrange
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "email2": "testuser@example.com",
            "password1": "Test-user1",
            "password2": "Test-user1",
        }

        # Act
        response = self.client.post(self.signup_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/signup.html")
        self.assertMessages(response, [])
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors["password1"]), 1)
        self.assertFormError(
            form,
            "password1",
            "The password is too similar to the username."
        )
        self.assertEqual(get_user_model().objects.count(), 0)
        self.assertEqual(EmailAddress.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_post_with_short_password_does_not_create_account_or_send_email_but_reports_errors(self):
        # Arrange
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "email2": "testuser@example.com",
            "password1": "Yfr_A1",
            "password2": "Yfr_A1",
        }

        # Act
        response = self.client.post(self.signup_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/signup.html")
        self.assertMessages(response, [])
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors["password1"]), 1)
        self.assertFormError(
            form,
            "password1",
            "This password is too short. It must contain at least 8 characters."
        )
        self.assertEqual(get_user_model().objects.count(), 0)
        self.assertEqual(EmailAddress.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_post_with_common_password_does_not_create_account_or_send_email_but_reports_errors(self):
        """
        This validator is not the best. It validates against django/contrib/auth/common-passwords.txt.gz,
        which contains 19640 entries, but a quick inspection shows that a password such as "Password123!"
        would pass simply because it has the added special character. We may add pwned-passwords-django
        to the mix to combat this in the future.
        """
        # Arrange
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "email2": "testuser@example.com",
            "password1": "Pass_2011",
            "password2": "Pass_2011",
        }

        # Act
        response = self.client.post(self.signup_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/signup.html")
        self.assertMessages(response, [])
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors["password1"]), 1)
        self.assertFormError(
            form,
            "password1",
            "This password is too common."
        )
        self.assertEqual(get_user_model().objects.count(), 0)
        self.assertEqual(EmailAddress.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_post_with_numeric_password_does_not_create_account_or_send_email_but_reports_errors(self):
        """
        This test will hit multiple errors: common, numeric, lacking letters, lacking lower, lacking special.
        """
        # Arrange
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "email2": "testuser@example.com",
            "password1": "31415926",
            "password2": "31415926",
        }

        # Act
        response = self.client.post(self.signup_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/signup.html")
        self.assertMessages(response, [])
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors["password1"]), 6)
        self.assertFormError(
            form,
            "password1",
            [
                "This password is too common.",
                "This password is entirely numeric.",
                "This password must contain at least 4 letters.",
                "This password must contain at least 1 upper case letter.",
                "This password must contain at least 1 lower case letter.",
                "This password must contain at least 1 special character."
            ]
        )
        self.assertEqual(get_user_model().objects.count(), 0)
        self.assertEqual(EmailAddress.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_post_with_valid_data_creates_account_and_sends_email(self):
        # Arrange
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "email2": "testuser@example.com",
            "password1": "Yfr_A0Qdk7W-s2s01Mec ",
            "password2": "Yfr_A0Qdk7W-s2s01Mec ",
        }

        # Act
        response = self.client.post(self.signup_url, data)

        # Assert
        self.assertRedirects(response, self.redirect_url)
        self.assertMessages(response, [Message(messages.INFO, f"Confirmation email sent to {data['email']}.")])
        self.assertEqual(get_user_model().objects.count(), 1)
        user = get_user_model().objects.get(username="testuser")
        email_record = EmailAddress.objects.filter(user=user).first()
        self.assertIsNotNone(email_record)
        self.assertEqual(email_record.email, data["email"])
        self.assertFalse(email_record.verified)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "[testserver] Please Confirm Your Email Address")
        self.assertEqual(mail.outbox[0].to, [user.email])


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
        self.assertTemplateUsed(response, "account/login.html")
        form = response.context_data["form"]
        self.assertEqual(form.fields["login"].label, "Username")
        self.assertEqual(form.fields["password"].label, "Password")

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
