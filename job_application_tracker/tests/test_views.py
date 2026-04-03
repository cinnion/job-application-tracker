import json
import os
from os import unlink
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class TestAboutView(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.build_info_path = os.path.join(settings.BASE_DIR, "build_info.json")
        cls.about_page_url = reverse("about")
        cls.template_used = "about.html"

    @classmethod
    def setUpTestData(cls):
        """
        Create our test users
        """
        super().setUpTestData()
        user_model = get_user_model()

        cls.test_user_1 = user_model.objects.create_user(
            username="testuser1",
            password="testuser1",
            email="testuser1@example.com"
        )

    def write_build_info_file(self):
        self.expected_build_info = {
            "BUILD_NUMBER": "Some build number",
            "BUILD_ID": "Some build id",
            "JOB_NAME": "Some job name",
            "BUILD_URL": "https://example.com/some-build-url",
            "GIT_COMMIT": "Some git commit",
            "GIT_BRANCH": "Some git branch",
            "GIT_TAG": "Some git tag",
            "BUILD_DATE": "Some build date"
        }

        try:
            with open(self.build_info_path, "w") as f:
                json.dump(self.expected_build_info, f)
        except PermissionError:
            print(f"Where were permission errors writing {"self.build_info_path"}."
                  " Please check permissions and rerun the tests.")
            raise
        except IsADirectoryError:
            print(f"There was a directory where {"self.build_info_path"} needs to go."
                  " Please remove it and rerun the tests.")
            raise
        except OSError as e:
            print(f"An OS related error occurred trying to write {"self.build_info_path"}: {e}")
            raise

    def tearDown(self):
        try:
            unlink(self.build_info_path)
        except FileNotFoundError:
            pass
        except PermissionError:
            print(f"There were permission errors removing {"self.build_path_info"}."
                  " Please remove this file so that the tests may proceed normally.")
            raise
        except OSError:
            print(f"For some reason, there is a directory where {"self.build_info_path"} should be")
            raise

    def test_nonexistent_file_returns_na_with_error(self):
        # Arrange
        assert not Path(self.build_info_path).exists(), f"Error: {"self.build_path_info"} should not exist."
        expected_build_info = {
            "Error": "The file 'build_info.json' was not found.",
            "BUILD_NUMBER": "N/A",
            "BUILD_ID": "N/A",
            "JOB_NAME": "N/A",
            "BUILD_URL": "N/A",
            "GIT_COMMIT": "N/A",
            "GIT_BRANCH": "N/A",
            "BUILD_DATE": "N/A",
        }

        # Act
        response = self.client.get(self.about_page_url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_used)
        self.assertEqual(response.context["BUILD_INFO"], expected_build_info)

    def test_junk_file_returns_na_with_error(self):
        # Arrange
        with open(self.build_info_path, "w") as f:
            f.write("This is some non-JSON garbage.\n")
        expected_build_info = {
            "Error": "Could not decode JSON fron the file build_info.json.",
            "BUILD_NUMBER": "N/A",
            "BUILD_ID": "N/A",
            "JOB_NAME": "N/A",
            "BUILD_URL": "N/A",
            "GIT_COMMIT": "N/A",
            "GIT_BRANCH": "N/A",
            "BUILD_DATE": "N/A",
        }

        # Act
        response = self.client.get(self.about_page_url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_used)
        self.assertEqual(response.context["BUILD_INFO"], expected_build_info)

    def test_actual_build_info_returns_info_with_no_error(self):
        # Arrange
        self.write_build_info_file()

        # Act
        response = self.client.get(self.about_page_url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_used)
        self.assertEqual(response.context["BUILD_INFO"], self.expected_build_info)


class TestHomeView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_url = reverse("home")
        cls.template_used = "home.html"

    def test_home_page_renders_correct_template(self):
        # Arrange

        # Act
        response = self.client.get(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_used)
