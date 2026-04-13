"""
Our class based tests for dealing with tests related directly to the User model and its
verification methods.
"""
import unittest

from django.test import TestCase

from users.models import User


class TestUserModel(TestCase):
    """
    This class tests our extensions to the default user model found in django.contrib.auth.models
    """

    def test_user_with_no_name_renders_as_expected(self):
        # Arrange
        user = User()

        # Act
        results = user.get_full_name()

        # Assert
        self.assertEqual(results, "")

    def test_user_with_just_first_name_renders_as_expected(self):
        # Arrange
        user = User(first_name="John")

        # Act
        results = user.get_full_name()

        # Assert
        self.assertEqual(results, "John")

    def test_user_with_first_and_last_name_renders_as_expected(self):
        # Arrange
        user = User(first_name="John", last_name="Crichton")

        # Act
        results = user.get_full_name()

        # Assert
        self.assertEqual("John Crichton", results)

    def test_user_with_first_middle_and_last_name_renders_as_expected(self):
        # Arrange
        user = User(first_name="John", middle_name="Robert", last_name="Crichton")

        # Arrange
        results = user.get_full_name()

        # Assert
        self.assertEqual("John Robert Crichton", results)

    def test_user_with_first_middle_initial_and_last_name_renders_as_expected(self):
        # Arrange
        user = User(first_name="John", middle_name="R", last_name="Crichton")

        # Arrange
        results = user.get_full_name()

        # Assert
        self.assertEqual("John R. Crichton", results)

    def test_user_with_first_middle_last_name_and_suffix_renders_as_expected(self):
        # Arrange
        user = User(first_name="John", middle_name="Robert", last_name="Crichton", suffix="Jr.")

        # Arrange
        results = user.get_full_name()

        # Assert
        self.assertEqual(results, "John Robert Crichton Jr.")

    def test_user_with_first_middle_initial_last_name_and_suffix_renders_as_expected(self):
        # Arrange
        user = User(first_name="John", middle_name="R", last_name="Crichton", suffix="Jr.")

        # Arrange
        results = user.get_full_name()

        # Assert
        self.assertEqual("John R. Crichton Jr.", results)

    def test_user_with_title_first_middle_last_name_and_suffix_renders_as_expected(self):
        # Arrange
        user = User(prefix="Commander", first_name="John", middle_name="Robert", last_name="Crichton", suffix="Jr.")

        # Arrange
        results = user.get_full_name()

        # Assert
        self.assertEqual("Commander John Robert Crichton Jr.", results)

    def test_user_with_title_first_middle_initial_last_name_and_suffix_renders_as_expected(self):
        # Arrange
        user = User(prefix="Commander", first_name="John", middle_name="R", last_name="Crichton", suffix="Jr.")

        # Arrange
        results = user.get_full_name()

        # Assert
        self.assertEqual("Commander John R. Crichton Jr.", results)


if __name__ == "__main__":
    unittest.main()
