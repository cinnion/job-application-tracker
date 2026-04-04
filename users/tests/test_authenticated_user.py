import unittest
from typing import cast

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.forms import (
    PasswordChangeForm
)
from django.forms.forms import BaseForm
from django.urls import reverse
from unittest_parametrize import parametrize

from core.test import TestCase
from core.tests.mixins import BaseAuthenticatedUserMixin
from users.forms import ProfileForm
from users.models import User


# noinspection DuplicatedCode
class TestAuthenticatedChangePasswordView(BaseAuthenticatedUserMixin, TestCase):
    """
    This test class tests the user authentication for the ChangePasswordView
    """
    test_url = reverse("password_change")
    expected_form = PasswordChangeForm
    expected_success_url = reverse("password_change_done")

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
            for field in user._meta.get_fields()
            if not field.is_relation
        }

    def test_superuser_can_get_change_password_form(self):
        # Arrange
        user = self.test_user_1
        client = self.client
        client.force_login(user)

        # Act
        response = client.get(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context_data["form"], PasswordChangeForm)

    def test_staff_can_get_change_password_form(self):
        # Arrange
        user = self.test_user_2
        client = self.client
        client.force_login(user)

        # Act
        response = client.get(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context_data["form"], PasswordChangeForm)

    def test_user_with_perm_can_get_change_password_form(self):
        # Arrange
        user = self.test_user_3
        client = self.client
        client.force_login(user)

        # Act
        response = client.get(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context_data["form"], PasswordChangeForm)

    def test_user_without_perm_cannot_get_change_password_form(self):
        # Arrange
        user = self.test_user_4
        client = self.client
        client.force_login(user)

        # Act
        response = client.get(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "403.html")

    def test_superuser_can_post_change_password_form(self):
        # Arrange
        user = self.test_user_1
        client = self.client
        client.force_login(user)
        user.refresh_from_db()  # Get a refreshed copy with the updated last_login
        orig_dict = self.get_user_fields(user)
        data = {
            "old_password": "testuser1",
            "new_password1": "Yfr_A0Qdk7W-s2s01Mec ",
            "new_password2": "Yfr_A0Qdk7W-s2s01Mec ",
        }

        # Act
        response = client.post(self.test_url, data)

        # Assert
        self.assertRedirects(
            response,
            self.expected_success_url,
            status_code=302,
            target_status_code=200
        )
        user.refresh_from_db()
        post_dict = self.get_user_fields(user)
        changed_fields = [k
                          for k in orig_dict.keys() & post_dict.keys()
                          if orig_dict[k] != post_dict[k]
                          ]
        self.assertEqual(changed_fields, ["password"])
        self.assertTrue(user.check_password(data["new_password1"]))

    def test_staff_bad_old_password_post_gets_errors(self):
        # Arrange
        user = self.test_user_2
        client = self.client
        client.force_login(user)
        user.refresh_from_db()  # Get a refreshed copy with the updated last_login
        orig_dict = self.get_user_fields(user)
        data = {
            "old_password": "asdf",
            "new_password1": "Yfr_A0Qdk7W-s2s01Mec ",
            "new_password2": "Yfr_A0Qdk7W-s2s01Mec ",
        }

        # Act
        response = client.post(self.test_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors["old_password"]), 1)
        self.assertFormError(
            form,
            "old_password",
            "Your old password was entered incorrectly. Please enter it again."
        )
        user.refresh_from_db()
        post_dict = self.get_user_fields(user)
        changed_fields = [k
                          for k in orig_dict.keys() & post_dict.keys()
                          if orig_dict[k] != post_dict[k]
                          ]
        self.assertEqual(changed_fields, [])
        self.assertFalse(user.check_password(data["new_password1"]))

    def test_staff_new_password_too_similar_post_gets_errors(self):
        # Arrange
        user = self.test_user_2
        client = self.client
        client.force_login(user)
        user.refresh_from_db()  # Get a refreshed copy with the updated last_login
        orig_dict = self.get_user_fields(user)
        data = {
            "old_password": "testuser2",
            "new_password1": "TestUser_2",
            "new_password2": "TestUser_2",
        }

        # Act
        response = client.post(self.test_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors["new_password2"]), 1)
        self.assertFormError(
            form,
            "new_password2",
            "The password is too similar to the username."
        )
        user.refresh_from_db()
        post_dict = self.get_user_fields(user)
        changed_fields = [k
                          for k in orig_dict.keys() & post_dict.keys()
                          if orig_dict[k] != post_dict[k]
                          ]
        self.assertEqual(changed_fields, [])
        self.assertFalse(user.check_password(data["new_password1"]))

    def test_staff_new_password_too_short_post_gets_errors(self):
        # Arrange
        user = self.test_user_2
        client = self.client
        client.force_login(user)
        user.refresh_from_db()  # Get a refreshed copy with the updated last_login
        orig_dict = self.get_user_fields(user)
        data = {
            "old_password": "testuser2",
            "new_password1": "aSdf_1",
            "new_password2": "aSdf_1",
        }

        # Act
        response = client.post(self.test_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors["new_password2"]), 1)
        self.assertFormError(
            form,
            "new_password2",
            "This password is too short. It must contain at least 8 characters."
        )
        user.refresh_from_db()
        post_dict = self.get_user_fields(user)
        changed_fields = [k
                          for k in orig_dict.keys() & post_dict.keys()
                          if orig_dict[k] != post_dict[k]
                          ]
        self.assertEqual(changed_fields, [])
        self.assertFalse(user.check_password(data["new_password1"]))

    # Commonly used password test would go here

    def test_staff_new_password_numeric_post_gets_errors(self):
        # Arrange
        user = self.test_user_2
        client = self.client
        client.force_login(user)
        user.refresh_from_db()  # Get a refreshed copy with the updated last_login
        orig_dict = self.get_user_fields(user)
        data = {
            "old_password": "testuser2",
            "new_password1": "987654321",
            "new_password2": "987654321",
        }

        # Act
        response = client.post(self.test_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors["new_password2"]), 6)
        self.assertFormError(
            form,
            "new_password2",
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
        self.assertFalse(user.check_password(data["new_password1"]))

    def test_staff_new_password_no_digits_post_gets_errors(self):
        # Arrange
        user = self.test_user_2
        client = self.client
        client.force_login(user)
        user.refresh_from_db()  # Get a refreshed copy with the updated last_login
        orig_dict = self.get_user_fields(user)
        data = {
            "old_password": "testuser2",
            "new_password1": "Hey Sparky!",
            "new_password2": "Hey Sparky!",
        }

        # Act
        response = client.post(self.test_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors["new_password2"]), 1)
        self.assertFormError(
            form,
            "new_password2",
            "This password must contain at least 1 digit."
        )
        user.refresh_from_db()
        post_dict = self.get_user_fields(user)
        changed_fields = [k
                          for k in orig_dict.keys() & post_dict.keys()
                          if orig_dict[k] != post_dict[k]
                          ]
        self.assertEqual(changed_fields, [])
        self.assertFalse(user.check_password(data["new_password1"]))

    def test_staff_new_password_no_special_post_gets_errors(self):
        # Arrange
        user = self.test_user_2
        client = self.client
        client.force_login(user)
        user.refresh_from_db()  # Get a refreshed copy with the updated last_login
        orig_dict = self.get_user_fields(user)
        data = {
            "old_password": "testuser2",
            "new_password1": "Hey Sparky1",
            "new_password2": "Hey Sparky1",
        }

        # Act
        response = client.post(self.test_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors["new_password2"]), 1)
        self.assertFormError(
            form,
            "new_password2",
            "This password must contain at least 1 special character."
        )
        user.refresh_from_db()
        post_dict = self.get_user_fields(user)
        changed_fields = [k
                          for k in orig_dict.keys() & post_dict.keys()
                          if orig_dict[k] != post_dict[k]
                          ]
        self.assertEqual(changed_fields, [])
        self.assertFalse(user.check_password(data["new_password1"]))

    def test_staff_can_post_change_password_form(self):
        # Arrange
        user = self.test_user_2
        client = self.client
        client.force_login(user)
        user.refresh_from_db()  # Get a refreshed copy with the updated last_login
        orig_dict = self.get_user_fields(user)
        data = {
            "old_password": "testuser2",
            "new_password1": "Yfr_A0Qdk7W-s2s01Mec ",
            "new_password2": "Yfr_A0Qdk7W-s2s01Mec ",
        }

        # Act
        response = client.post(self.test_url, data)

        # Assert
        self.assertRedirects(
            response,
            self.expected_success_url,
            status_code=302,
            target_status_code=200
        )
        user.refresh_from_db()
        post_dict = self.get_user_fields(user)
        changed_fields = [k
                          for k in orig_dict.keys() & post_dict.keys()
                          if orig_dict[k] != post_dict[k]
                          ]
        self.assertEqual(changed_fields, ["password"])
        self.assertTrue(user.check_password(data["new_password1"]))

    def test_user_with_perm_can_post_change_password_form(self):
        # Arrange
        user = self.test_user_3
        client = self.client
        client.force_login(user)
        user.refresh_from_db()  # Get a refreshed copy with the updated last_login
        orig_dict = self.get_user_fields(user)
        data = {
            "old_password": "testuser3",
            "new_password1": "Yfr_A0Qdk7W-s2s01Mec ",
            "new_password2": "Yfr_A0Qdk7W-s2s01Mec ",
        }

        # Act
        response = client.post(self.test_url, data)

        # Assert
        self.assertRedirects(
            response,
            self.expected_success_url,
            status_code=302,
            target_status_code=200
        )
        user.refresh_from_db()
        post_dict = self.get_user_fields(user)
        changed_fields = [k
                          for k in orig_dict.keys() & post_dict.keys()
                          if orig_dict[k] != post_dict[k]
                          ]
        self.assertEqual(changed_fields, ["password"])
        self.assertTrue(user.check_password(data["new_password1"]))

    def test_user_without_perm_cannot_post_change_password_form(self):
        # Arrange
        user = self.test_user_4
        client = self.client
        client.force_login(user)
        user.refresh_from_db()  # Get a refreshed copy with the updated last_login
        orig_dict = self.get_user_fields(user)
        data = {
            "old_password": "testuser4",
            "new_password1": "Yfr_A0Qdk7W-s2s01Mec ",
            "new_password2": "Yfr_A0Qdk7W-s2s01Mec ",
        }

        # Act
        response = client.post(self.test_url, data)

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
        self.assertFalse(user.check_password(data["new_password1"]))

    def test_put_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.put(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 405)

    def test_patch_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.patch(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 405)

    def test_delete_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.delete(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 405)

    def test_head_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.head(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 405)

    def test_options_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.options(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 405)


class TestAuthenticatedEditProfileView(BaseAuthenticatedUserMixin, TestCase):
    """
    This class tests our extensions to the default user model found in django.contrib.auth.models
    """
    test_url = reverse("profile")

    expected_form = ProfileForm()
    expected_template = "registration/edit_profile.html"
    expected_redirect_url = reverse("home")

    def assert_form_fields_equal(self, form: BaseForm, data: dict) -> None:
        for key, value in data.items():
            self.assertEqual(form[key].value(), value,
                             f"""The "{key}" field does not match: "{form[key].value()}" != "{value}".""")

    @parametrize(
        "user_attr",
        [
            "test_user_1",
            "test_user_2",
        ]
    )
    def test_get_a_user_view_gets_correct_profile(self, user_attr):
        # Arrange
        user = getattr(self, user_attr)
        client = self.client
        client.force_login(user)
        expected_user_data = {f: getattr(user, f) for f in ProfileForm.field_order if hasattr(user, f)}

        # Act
        response = self.client.get(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.expected_template)
        self.assertEqual(response.context_data["object"], user)
        form = response.context_data["form"]
        self.assert_form_fields_equal(form, expected_user_data)

    def test_post_good_data_new_data_gets_saved(self):
        # Arrange
        user = cast(User, self.test_user_1)
        client = self.client
        client.force_login(user)
        data = {
            "username": "newuser",
            "prefix": "New prefix",
            "first_name": "New first",
            "middle_name": "New middle",
            "last_name": "New last",
            "suffix": "New suffix",
            "email": "testuser5@example.com",
        }
        old_user = user

        # Act
        response = client.post(self.test_url, data)
        user.refresh_from_db()

        # Assert
        self.assertRedirects(
            response,
            self.expected_redirect_url,
            status_code=302,
            target_status_code=200
        )
        self.assertEqual(user.username, data["username"])
        self.assertEqual(user.prefix, data["prefix"])
        self.assertEqual(user.first_name, data["first_name"])
        self.assertEqual(user.middle_name, data["middle_name"])
        self.assertEqual(user.last_name, data["last_name"])
        self.assertEqual(user.suffix, data["suffix"])
        self.assertEqual(user.email, data["email"])
        self.assertEqual(user.password, old_user.password)

    @parametrize(
        "test_username",
        [
            "new username",
            "$newusername",
            'new"username',
            "new's username",
        ],
    )
    def test_post_bad_username_expected_error_returned(self, test_username: str) -> None:
        # Arrange
        user = cast(User, self.test_user_1)
        client = self.client
        client.force_login(user)
        data = {
            "username": test_username,
            "prefix": "New prefix",
            "first_name": "New first",
            "middle_name": "New middle",
            "last_name": "New last",
            "suffix": "New suffix",
            "email": "testuser5@example.com",
        }
        old_user = user

        # Act
        response = client.post(self.test_url, data)
        user.refresh_from_db()

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.expected_template)
        form = response.context_data["form"]
        self.assert_form_fields_equal(form, data)
        self.assertEqual(len(form.errors), 1)
        self.assertFormError(
            form,
            "username",
            "Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters."
        )
        self.assertEqual(user, old_user)

    @parametrize(
        "add_data",
        [
            {
                "password": "Some ignored password"
            },
            {
                "old_password": "Some junk",
                "new_password1": "More ignored junk",
                "new_password2": "More ignored junk"
            }
        ]
    )
    def test_post_attempted_password_overwrite_password_unchanged(self, add_data) -> None:
        # Arrange
        user = cast(User, self.test_user_1)
        client = self.client
        client.force_login(user)
        data = {
            "username": "New-username",
            "prefix": "New prefix",
            "first_name": "New first",
            "middle_name": "New middle",
            "last_name": "New last",
            "suffix": "New suffix",
            "email": "testuser5@example.com",
        }
        data = data | add_data
        old_user = user

        # Act
        response = client.post(self.test_url, data)
        user.refresh_from_db()

        # Assert
        self.assertRedirects(
            response,
            self.expected_redirect_url,
            status_code=302,
            target_status_code=200
        )
        self.assertEqual(user.password, old_user.password)

    def test_post_attempted_gain_is_staff_is_staff_unchanged(self) -> None:
        # Arrange
        user = cast(User, self.test_user_4)
        client = self.client
        client.force_login(user)
        data = {
            "username": "New-username",
            "prefix": "New prefix",
            "first_name": "New first",
            "middle_name": "New middle",
            "last_name": "New last",
            "suffix": "New suffix",
            "email": "testuser5@example.com",
            "is_staff": True
        }
        old_user = user

        # Act
        response = client.post(self.test_url, data)
        user.refresh_from_db()

        # Assert
        self.assertRedirects(
            response,
            self.expected_redirect_url,
            status_code=302,
            target_status_code=200
        )
        self.assertEqual(user.is_staff, old_user.is_staff)

    def test_post_attempted_gain_is_superuser_is_superuser_unchanged(self) -> None:
        # Arrange
        user = cast(User, self.test_user_4)
        client = self.client
        client.force_login(user)
        data = {
            "username": "New-username",
            "prefix": "New prefix",
            "first_name": "New first",
            "middle_name": "New middle",
            "last_name": "New last",
            "suffix": "New suffix",
            "email": "testuser5@example.com",
            "is_superuser": True
        }
        old_user = user

        # Act
        response = client.post(self.test_url, data)
        user.refresh_from_db()

        # Assert
        self.assertRedirects(
            response,
            self.expected_redirect_url,
            status_code=302,
            target_status_code=200
        )
        self.assertEqual(user.is_superuser, old_user.is_superuser)

    def test_put_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.put(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 405)

    def test_patch_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.patch(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 405)

    def test_delete_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.delete(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 405)

    def test_head_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.head(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 405)

    def test_options_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.options(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 405)


if __name__ == "__main__":
    unittest.main()
