"""
Test the functionality of users resetting their password to make sure that we
get things like the right templates.
"""
import unittest
from datetime import datetime
from textwrap import dedent
from unittest import mock

from allauth.account import app_settings
from allauth.account.forms import (
    EmailAwarePasswordResetTokenGenerator,
    ResetPasswordKeyForm,
    ResetPasswordForm
)
from allauth.account.utils import user_pk_to_url_str
from allauth.account.views import INTERNAL_RESET_SESSION_KEY
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.messages import (
    Message,
    constants as messages
)
from django.contrib.messages.test import MessagesTestMixin
from django.core import mail
from django.urls import reverse

from core.test import TestCase


# noinspection DuplicatedCode
class TestUnauthenticatedUserPasswordResetView(MessagesTestMixin, TestCase):
    """
    Test the functionality of users resetting their password to make sure that
    we get things like the right layout templates.
    """
    fixtures = ["core/tests/fixtures/users.json"]
    url = reverse("account_reset_password")

    @staticmethod
    def get_user_fields(user: AbstractBaseUser) -> dict:
        """
        Get a dictionary of User model field values, so that it is disconnected from the database and can be used
        for later verification.

        Args:
            user: AbstractBaseUser - A user instance.

        Returns:
            A dict of keys with values for the fields of the User class.
        """
        return {
            field.name: getattr(user, field.name)
            for field in user._meta.get_fields()  # pylint: disable=protected-access
            if not field.is_relation
        }

    @staticmethod
    def setup_uidb36_and_key(username: str) -> tuple[AbstractBaseUser, str, str]:
        """
        Generate the uidb36 and key for a password reset, with an optionally
        mocked django.contrib.auth.tokens.PasswordResetGenerator._now()
        returning a specific time.

        Args:
            username: The username we are testing against.

        Returns:
             A tuple consisting of the user, the uidb36 formatted UID, and the
             reset key.
        """
        user = get_user_model().objects.get(username=username)
        uidb36 = user_pk_to_url_str(user)
        key = EmailAwarePasswordResetTokenGenerator().make_token(user)

        return user, uidb36, key

    def setup_uidb36_and_key_with_reset_url(
            self,
            username: str
    ) -> tuple[AbstractBaseUser, str, str, str]:
        """
        Like setup_uidb36_and_key, but includes the URL for starting the
        password reset process.

        Args:
            username: The username we are testing against.

        Returns:
              A tuple consisting of the user, the uidb36 formatted UID, the
              reset key and the URL to start the reset.
        """
        user, uidb36, key = self.setup_uidb36_and_key(username)
        url = reverse("account_reset_password_from_key", kwargs={"uidb36": uidb36, "key": key})

        return user, uidb36, key, url

    def setup_uidb36_and_key_with_set_url(
            self,
            username: str
    ) -> tuple[AbstractBaseUser, str, str, str]:
        """
        Like setup_uidb36_and_key, but includes the URL for doing the actual
        password reset process.

        Args:
            username: The username we are testing against.

        Returns:
              A tuple consisting of the user, the uidb36 formatted UID, the
              reset key and the URL to do the actual reset.
        """
        user, uidb36, key = self.setup_uidb36_and_key(username)
        url = reverse("account_reset_password_from_key", kwargs={"uidb36": uidb36, "key": "set-password"})

        return user, uidb36, key, url

    def test_get_password_reset_returns_initial_form_rendered_into_user_admin_layout(self):
        # Arrange

        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "master.html")
        self.assertTemplateUsed(response, "user-master.html")
        self.assertTemplateUsed(response, f"account/password_reset.{app_settings.TEMPLATE_EXTENSION}")
        form = response.context_data['form']
        self.assertIsInstance(form, ResetPasswordForm)
        self.assertEqual(len(form.fields), 1)
        self.assertEqual(form.fields["email"].label, "Email")

    def test_post_reset_password_of_invalid_email_returns_proper_screen_not_enumerating_account(self):
        # Arrange
        data = {
            "email": "not-a-user@example.com"
        }

        # Act
        response = self.client.post(self.url, data, follow=True)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "master.html")
        self.assertTemplateUsed(response, "user-master.html")
        self.assertTemplateUsed(response, f"account/password_reset_done.{app_settings.TEMPLATE_EXTENSION}")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "[testserver] Unknown Account")
        self.assertEqual(mail.outbox[0].to, [data["email"]])
        self.assertIn(dedent("""\
                        Hello from testserver!

                        You are receiving this email because you, or someone else, tried to access an account with email not-a-user@example.com. However, we do not have any record of such an account in our database.

                        This mail can be safely ignored if you did not initiate this action.

                        If it was you, you can sign up for an account using the link below.

                        http://testserver/users/signup/"""),
                      mail.outbox[0].body)

    @mock.patch("django.contrib.auth.tokens.PasswordResetTokenGenerator._now")
    def test_post_reset_password_of_valid_email_with_permissions_returns_proper_screen_not_enumerating_account(self,
                                                                                                               mock_now):
        # Arrange
        fixed_now = datetime(2026, 1, 1, 12, 0, 0)
        mock_now.return_value = fixed_now
        user, _, _, reset_url = self.setup_uidb36_and_key_with_reset_url("testuser3")
        data = {
            "email": "testuser3@example.com"
        }

        # Act
        response = self.client.post(self.url, data, follow=True)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "master.html")
        self.assertTemplateUsed(response, "user-master.html")
        self.assertTemplateUsed(response, f"account/password_reset_done.{app_settings.TEMPLATE_EXTENSION}")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "[testserver] Password Reset Email")
        self.assertEqual(mail.outbox[0].to, [data["email"]])
        self.assertIn(dedent(f"""\
                            Hello from testserver!

                            You're receiving this email because you or someone else has requested a password reset for your user account.
                            It can be safely ignored if you did not request a password reset. Click the link below to reset your password.

                            http://testserver{reset_url}

                            In case you forgot, your username is {user.username}.

                            Thank you for using testserver!"""),
                      mail.outbox[0].body
                      )

    @mock.patch("django.contrib.auth.tokens.PasswordResetTokenGenerator._now")
    def test_post_reset_password_of_valid_email_without_permissions_returns_proper_screen_not_enumerating_account(self,
                                                                                                                  mock_now):
        # Arrange
        fixed_now = datetime(2026, 1, 1, 12, 0, 0)
        mock_now.return_value = fixed_now
        user, _, _, reset_url = self.setup_uidb36_and_key_with_reset_url("testuser4")
        data = {
            "email": "testuser4@example.com"
        }

        # Act
        response = self.client.post(self.url, data, follow=True)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "master.html")
        self.assertTemplateUsed(response, "user-master.html")
        self.assertTemplateUsed(response, f"account/password_reset_done.{app_settings.TEMPLATE_EXTENSION}")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "[testserver] Password Reset Email")
        self.assertEqual(mail.outbox[0].to, [data["email"]])
        self.assertIn(dedent(f"""\
                            Hello from testserver!

                            You're receiving this email because you or someone else has requested a password reset for your user account.
                            It can be safely ignored if you did not request a password reset. Click the link below to reset your password.

                            http://testserver{reset_url}

                            In case you forgot, your username is {user.username}.

                            Thank you for using testserver!"""),
                      mail.outbox[0].body
                      )

    def test_get_reset_password_with_invalid_key_returns_error_and_does_not_prep_session(self):
        # Arrange
        _, uidb36, key = self.setup_uidb36_and_key("testuser1")
        timestamp, token = key.rsplit("-")
        badkey = "-".join([timestamp, token[::-1]])
        url = reverse("account_reset_password_from_key", kwargs={"uidb36": uidb36, "key": badkey})

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "master.html")
        self.assertTemplateUsed(response, "user-master.html")
        self.assertTemplateUsed(response, f"account/password_reset_from_key.{app_settings.TEMPLATE_EXTENSION}")
        self.assertContains(response, "<h4>Bad Token</h4>", html=True)
        self.assertContains(response,
                            "The password reset link was invalid, possibly because it has already been used.  Please request a <a href=\"{reset_url}\">new password reset</a>.",
                            html=True)
        self.assertIsNone(self.client.session.get(INTERNAL_RESET_SESSION_KEY, None))

    def test_get_reset_password_with_expired_key_returns_error_and_does_not_prep_session(self):
        # Arrange
        with mock.patch.object(PasswordResetTokenGenerator, "_now", return_value=datetime(2026, 1, 1, 12, 0, 0)):
            _, uidb36, key = self.setup_uidb36_and_key("testuser1")
        url = reverse("account_reset_password_from_key", kwargs={"uidb36": uidb36, "key": key})
        reset_url = reverse("account_reset_password")

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "master.html")
        self.assertTemplateUsed(response, "user-master.html")
        self.assertTemplateUsed(response, f"account/password_reset_from_key.{app_settings.TEMPLATE_EXTENSION}")
        self.assertContains(response, "<h4>Bad Token</h4>", html=True)
        self.assertContains(response,
                            f"The password reset link was invalid, possibly because it has already been used.  Please request a <a href=\"{reset_url}\">new password reset</a>.",
                            html=True)
        self.assertIsNone(self.client.session.get(INTERNAL_RESET_SESSION_KEY, None))

    def test_get_reset_password_with_valid_key_returns_form_and_preps_session(self):
        # Arrange
        _, uidb36, key, url = self.setup_uidb36_and_key_with_reset_url("testuser2")
        redirect_url = reverse("account_reset_password_from_key", kwargs={"uidb36": uidb36, "key": "set-password"})

        # Act
        response = self.client.get(url, follow=True)

        # Assert
        self.assertRedirects(response, redirect_url)
        self.assertTemplateUsed(response, "master.html")
        self.assertTemplateUsed(response, "user-master.html")
        self.assertTemplateUsed(response, f"account/password_reset_from_key.{app_settings.TEMPLATE_EXTENSION}")
        self.assertContains(response, "<h4>Change Password</h4>", html=True)
        form = response.context_data["form"]
        self.assertIsInstance(form, ResetPasswordKeyForm)
        self.assertEqual(self.client.session.get(INTERNAL_RESET_SESSION_KEY, ""), key)

    def test_staff_post_password_reset_key_form_too_similar_password_gets_error(self):
        # Arrange
        data = {
            "password1": "TestUser_2 ",
            "password2": "TestUser_2 ",
        }
        user, _, key, url = self.setup_uidb36_and_key_with_set_url("testuser2")
        orig_dict = self.get_user_fields(user)
        session = self.client.session
        session[INTERNAL_RESET_SESSION_KEY] = key
        session.save()

        # Act
        response = self.client.post(url, data, follow=True)

        # Assert
        self.assertEqual(response.status_code, 200)
        form = response.context_data["form"]
        self.assertIsInstance(form, ResetPasswordKeyForm)
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors["password1"]), 1)
        self.assertFormError(
            form,
            "password1",
            "The password is too similar to the username."
        )
        user.refresh_from_db()
        post_dict = self.get_user_fields(user)
        changed_fields = [k
                          for k in orig_dict.keys() & post_dict.keys()
                          if orig_dict[k] != post_dict[k]
                          ]
        self.assertEqual(changed_fields, [])
        self.assertFalse(user.check_password(data["password1"]))
        self.assertEqual(self.client.session.get(INTERNAL_RESET_SESSION_KEY, ""), key)

    def test_staff_post_password_reset_key_form_too_short_password_gets_error(self):
        # Arrange
        data = {
            "password1": "aSdf_1",
            "password2": "aSdf_1",
        }
        user, _, key, url = self.setup_uidb36_and_key_with_set_url("testuser2")
        orig_dict = self.get_user_fields(user)
        session = self.client.session
        session[INTERNAL_RESET_SESSION_KEY] = key
        session.save()

        # Act
        response = self.client.post(url, data, follow=True)

        # Assert
        self.assertEqual(response.status_code, 200)
        form = response.context_data["form"]
        self.assertIsInstance(form, ResetPasswordKeyForm)
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors["password1"]), 1)
        self.assertFormError(
            form,
            "password1",
            "This password is too short. It must contain at least 8 characters."
        )
        user.refresh_from_db()
        post_dict = self.get_user_fields(user)
        changed_fields = [k
                          for k in orig_dict.keys() & post_dict.keys()
                          if orig_dict[k] != post_dict[k]
                          ]
        self.assertEqual(changed_fields, [])
        self.assertFalse(user.check_password(data["password1"]))
        self.assertEqual(self.client.session.get(INTERNAL_RESET_SESSION_KEY, ""), key)

    def test_staff_post_password_reset_key_form_numeric_password_gets_error(self):
        # Arrange
        data = {
            "password1": "987654321",
            "password2": "987654321",
        }
        user, _, key, url = self.setup_uidb36_and_key_with_set_url("testuser2")
        orig_dict = self.get_user_fields(user)
        session = self.client.session
        session[INTERNAL_RESET_SESSION_KEY] = key
        session.save()

        # Act
        response = self.client.post(url, data, follow=True)

        # Assert
        self.assertEqual(response.status_code, 200)
        form = response.context_data["form"]
        self.assertIsInstance(form, ResetPasswordKeyForm)
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
        user.refresh_from_db()
        post_dict = self.get_user_fields(user)
        changed_fields = [k
                          for k in orig_dict.keys() & post_dict.keys()
                          if orig_dict[k] != post_dict[k]
                          ]
        self.assertEqual(changed_fields, [])
        self.assertFalse(user.check_password(data["password1"]))
        self.assertEqual(self.client.session.get(INTERNAL_RESET_SESSION_KEY, ""), key)

    def test_staff_post_password_reset_key_form_no_digits_password_gets_error(self):
        # Arrange
        data = {
            "password1": "Hey Sparky!",
            "password2": "Hey Sparky!",
        }
        user, _, key, url = self.setup_uidb36_and_key_with_set_url("testuser2")
        orig_dict = self.get_user_fields(user)
        session = self.client.session
        session[INTERNAL_RESET_SESSION_KEY] = key
        session.save()

        # Act
        response = self.client.post(url, data, follow=True)

        # Assert
        self.assertEqual(response.status_code, 200)
        form = response.context_data["form"]
        self.assertIsInstance(form, ResetPasswordKeyForm)
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors["password1"]), 1)
        self.assertFormError(
            form,
            "password1",
            "This password must contain at least 1 digit."
        )
        user.refresh_from_db()
        post_dict = self.get_user_fields(user)
        changed_fields = [k
                          for k in orig_dict.keys() & post_dict.keys()
                          if orig_dict[k] != post_dict[k]
                          ]
        self.assertEqual(changed_fields, [])
        self.assertFalse(user.check_password(data["password1"]))
        self.assertEqual(self.client.session.get(INTERNAL_RESET_SESSION_KEY, ""), key)

    def test_staff_post_password_reset_key_form_no_special_password_gets_error(self):
        # Arrange
        data = {
            "password1": "HeySparky1",
            "password2": "HeySparky1",
        }
        user, _, key, url = self.setup_uidb36_and_key_with_set_url("testuser2")
        orig_dict = self.get_user_fields(user)
        session = self.client.session
        session[INTERNAL_RESET_SESSION_KEY] = key
        session.save()

        # Act
        response = self.client.post(url, data, follow=True)

        # Assert
        self.assertEqual(response.status_code, 200)
        form = response.context_data["form"]
        self.assertIsInstance(form, ResetPasswordKeyForm)
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors["password1"]), 1)
        self.assertFormError(
            form,
            "password1",
            "This password must contain at least 1 special character."
        )
        user.refresh_from_db()
        post_dict = self.get_user_fields(user)
        changed_fields = [k
                          for k in orig_dict.keys() & post_dict.keys()
                          if orig_dict[k] != post_dict[k]
                          ]
        self.assertEqual(changed_fields, [])
        self.assertFalse(user.check_password(data["password1"]))
        self.assertEqual(self.client.session.get(INTERNAL_RESET_SESSION_KEY, ""), key)

    def test_staff_post_password_reset_key_form_valid_password_changes_and_redirects_to_reset_done_page(self):
        # Arrange
        data = {
            "password1": "Yfr_A0Qdk7W-s2s01Mec ",
            "password2": "Yfr_A0Qdk7W-s2s01Mec ",
        }
        user, _, key, url = self.setup_uidb36_and_key_with_set_url("testuser2")
        orig_dict = self.get_user_fields(user)
        session = self.client.session
        session[INTERNAL_RESET_SESSION_KEY] = key
        session.save()
        redirect_url = reverse("account_reset_password_from_key_done")

        # Act
        response = self.client.post(url, data, follow=True)

        # Assert
        self.assertRedirects(response, redirect_url)
        self.assertMessages(response, [Message(messages.SUCCESS, "Password successfully changed.")])
        self.assertContains(response, "<h4>Change Password</h4>", html=True)
        self.assertContains(response, "Your password is now changed.")
        user.refresh_from_db()
        post_dict = self.get_user_fields(user)
        changed_fields = [k
                          for k in orig_dict.keys() & post_dict.keys()
                          if orig_dict[k] != post_dict[k]
                          ]
        self.assertEqual(changed_fields, ["password"])
        self.assertTrue(user.check_password(data["password1"]))

    def test_user_with_perm_post_password_reset_key_form_valid_password_changes_and_redirects_to_reset_done_page(self):
        # Arrange
        data = {
            "password1": "Yfr_A0Qdk7W-s2s01Mec ",
            "password2": "Yfr_A0Qdk7W-s2s01Mec ",
        }
        user, _, key, url = self.setup_uidb36_and_key_with_set_url("testuser3")
        orig_dict = self.get_user_fields(user)
        session = self.client.session
        session[INTERNAL_RESET_SESSION_KEY] = key
        session.save()
        redirect_url = reverse("account_reset_password_from_key_done")

        # Act
        response = self.client.post(url, data, follow=True)

        # Assert
        self.assertRedirects(response, redirect_url)
        self.assertMessages(response, [Message(messages.SUCCESS, "Password successfully changed.")])
        self.assertContains(response, "<h4>Change Password</h4>", html=True)
        self.assertContains(response, "Your password is now changed.")
        user.refresh_from_db()
        post_dict = self.get_user_fields(user)
        changed_fields = [k
                          for k in orig_dict.keys() & post_dict.keys()
                          if orig_dict[k] != post_dict[k]
                          ]
        self.assertEqual(changed_fields, ["password"])
        self.assertTrue(user.check_password(data["password1"]))

    def test_user_without_perm_post_password_reset_key_form_valid_password_does_not_change_and_raises_permission_denied(
            self):
        # Arrange
        data = {
            "password1": "Yfr_A0Qdk7W-s2s01Mec ",
            "password2": "Yfr_A0Qdk7W-s2s01Mec ",
        }
        user, _, key, url = self.setup_uidb36_and_key_with_set_url("testuser4")
        orig_dict = self.get_user_fields(user)
        session = self.client.session
        session[INTERNAL_RESET_SESSION_KEY] = key
        session.save()

        # Act
        with self.assertLogs('users.views', level='INFO') as cm:
            response = self.client.post(url, data, follow=True)
            self.assertIn("ERROR:users.views:Someone at ", cm.output[0])

        # Assert
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "403.html")
        user.refresh_from_db()
        post_dict = self.get_user_fields(user)
        changed_fields = [k
                          for k in orig_dict.keys() & post_dict.keys()
                          if orig_dict[k] != post_dict[k]
                          ]
        self.assertEqual(changed_fields, [])
        self.assertFalse(user.check_password(data["password1"]))


if __name__ == '__main__':
    unittest.main()
