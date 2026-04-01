import unittest

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse


class BaseAuthenticatedUserApplication(TestCase):
    """
    These methods are common to all the tests with an authenticated user client.
    """

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

        cls.test_user_2 = user_model.objects.create_user(
            username="testuser2",
            password="testuser2",
            email="testuser2@example.com"
        )

    def setUp(self):
        """
        Create our authenticated client for use by the individual tests.
        """
        self.client = Client()
        self.client.force_login(self.test_user_1)


class AuthenticatedUserApplicationListTests(BaseAuthenticatedUserApplication):
    """
    These tests are for the application list page.
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up our common test_url.
        """
        super().setUpClass()
        cls.test_url = reverse("applications:application-list")

    def test_get_request_gets_application_list_template(self):
        # Arrange

        # Act
        response = self.client.get(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationList.html")

    def test_post_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.post(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 405)

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


class AuthenticatedUserNewApplicationDetailsTests(BaseAuthenticatedUserApplication):
    """
    Test the various submissions of new job applications, to verify that we see the errors or redirections expected.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_url = reverse("applications:new-application")
        cls.list_url = reverse("applications:application-list")

    def test_get_request_gets_empty_new_application_template(self):
        # Arrange

        # Act
        response = self.client.get(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationDetails.html")

    def test_post_request_with_no_data_gets_errors(self):
        # Arrange
        data = {}

        # Act
        response = self.client.post(self.test_url, data)
        form = response.context_data["form"]

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationDetails.html")
        self.assertEqual(len(form.errors), 3, "There should be three fields with errors")
        self.assertFormError(
            form,
            "company",
            "This field is required."
        )
        self.assertFormError(
            form,
            "title",
            "This field is required."
        )
        self.assertFormError(
            form,
            "interviews",
            "This field is required."
        )

    def test_post_request_with_blank_company_gets_errors(self):
        # Arrange
        data = {
            "company": "",
            "title": "Some title",
            "interviews": 0,
        }

        # Act
        response = self.client.post(self.test_url, data)
        form = response.context_data["form"]

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationDetails.html")
        self.assertEqual(len(form.errors), 1, "There should be one field with errors")
        self.assertFormError(
            form,
            "company",
            "This field is required."
        )

    def test_post_request_with_blank_title_gets_errors(self):
        # Arrange
        data = {
            "company": "Some company",
            "title": "",
            "interviews": 0,
        }

        # Act
        response = self.client.post(self.test_url, data)
        form = response.context_data["form"]

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationDetails.html")
        self.assertEqual(len(form.errors), 1, "There should be one field with errors")
        self.assertFormError(
            form,
            "title",
            "This field is required."
        )

    def test_post_request_with_blank_interviews_gets_errors(self):
        # Arrange
        data = {
            "company": "Some company",
            "title": "Some title",
            "interviews": "",
        }

        # Act
        response = self.client.post(self.test_url, data)
        form = response.context_data["form"]

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationDetails.html")
        self.assertEqual(len(form.errors), 1, "There should be one field with errors")
        self.assertFormError(
            form,
            "interviews",
            "This field is required."
        )

    def test_post_request_with_bad_when_gets_errors(self):
        # Arrange
        data = {
            "when": "asdf",
            "company": "Some company",
            "title": "Some title",
            "interviews": 0,
        }

        # Act
        response = self.client.post(self.test_url, data)
        form = response.context_data["form"]

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationDetails.html")
        self.assertEqual(len(form.errors), 1, "There should only be one field with an error")
        self.assertFormError(
            form,
            "when",
            "Enter a valid date."
        )

    # TODO: Add validation and tests for future dates.

    def test_post_request_with_bad_posting_url_gets_errors(self):
        # Arrange
        data = {
            "when": "1999-12-31",
            "company": "Some company",
            "title": "Some title",
            "posting": "asdf",
            "interviews": 0,
        }

        # Act
        response = self.client.post(self.test_url, data)
        form = response.context_data["form"]

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationDetails.html")
        self.assertEqual(len(form.errors), 1, "There should only be one field with an error")
        self.assertFormError(
            form,
            "posting",
            "Enter a valid URL."
        )

    def test_post_request_with_empty_posting_url_gets_no_errors(self):
        # Arrange
        data = {
            "when": "1999-12-31",
            "company": "Some company",
            "title": "Some title",
            "posting": "",
            "interviews": 0,
        }

        # Act
        response = self.client.post(self.test_url, data)

        # Assert
        self.assertRedirects(
            response,
            self.list_url,
            status_code=302,
            target_status_code=200
        )

    def test_post_request_with_good_posting_url_gets_no_errors(self):
        # Arrange
        data = {
            "when": "1999-12-31",
            "company": "Some company",
            "title": "Some title",
            "posting": "https://example.com",
            "interviews": 0,
        }

        # Act
        response = self.client.post(self.test_url, data)

        # Assert
        self.assertRedirects(
            response,
            self.list_url,
            status_code=302,
            target_status_code=200
        )

    def test_post_request_with_empty_confirm_url_gets_no_errors(self):
        # Arrange
        data = {
            "when": "1999-12-31",
            "company": "Some company",
            "title": "Some title",
            "confirm": "",
            "interviews": 0,
        }

        # Act
        response = self.client.post(self.test_url, data)

        # Assert
        self.assertRedirects(
            response,
            self.list_url,
            status_code=302,
            target_status_code=200
        )

    def test_post_request_with_good_confirm_url_gets_no_errors(self):
        # Arrange
        data = {
            "when": "1999-12-31",
            "company": "Some company",
            "title": "Some title",
            "confirm": "https://example.com",
            "interviews": 0,
        }

        # Act
        response = self.client.post(self.test_url, data)

        # Assert
        self.assertRedirects(
            response,
            self.list_url,
            status_code=302,
            target_status_code=200
        )

    def test_post_request_with_bad_interviews_value_gets_errors(self):
        # Arrange
        data = {
            "when": "1999-12-31",
            "company": "Some company",
            "title": "Some title",
            "interviews": "asdf",
        }

        # Act
        response = self.client.post(self.test_url, data)
        form = response.context_data["form"]

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationDetails.html")
        self.assertEqual(len(form.errors), 1, "There should only be one field with an error")
        self.assertFormError(
            form,
            "interviews",
            "Enter a whole number."
        )

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
