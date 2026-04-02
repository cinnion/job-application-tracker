"""
These are tests which deal with authenticated user requests for the URLs associated with this package.
"""
import unittest
from typing import Any

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from applications.forms import EditApplication
from applications.models import JobApplication


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

    def test_list_get_request_gets_application_list_template(self):
        # Arrange

        # Act
        response = self.client.get(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationList.html")

    def test_list_post_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.post(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 405)

    def test_list_put_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.put(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 405)

    def test_list_patch_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.patch(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 405)

    def test_list_delete_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.delete(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 405)

    def test_list_head_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.head(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 405)

    def test_list_options_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.options(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 405)


# noinspection DuplicatedCode
class AuthenticatedUserNewApplicationDetailsTests(BaseAuthenticatedUserApplication):
    """
    Test the various submissions of new job applications, to verify that we see the errors or redirections expected.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_url = reverse("applications:new-application")
        cls.list_url = reverse("applications:application-list")

    def assert_no_record(self):
        """
        Assert that no record has been written.
        """
        self.assertEqual(JobApplication.objects.count(), 0)

    def test_new_get_request_gets_empty_new_application_template(self):
        # Arrange

        # Act
        response = self.client.get(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationDetails.html")

    def test_new_post_request_with_no_data_gets_errors(self):
        # Arrange
        data = {}

        # Act
        response = self.client.post(self.test_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationDetails.html")
        form = response.context_data["form"]
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
        self.assert_no_record()

    def test_new_post_request_with_bad_when_gets_errors(self):
        # Arrange
        data = {
            "when": "asdf",
            "company": "Some company",
            "title": "Some title",
            "interviews": 0,
        }

        # Act
        response = self.client.post(self.test_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationDetails.html")
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1, "There should only be one field with an error")
        self.assertFormError(
            form,
            "when",
            "Enter a valid date."
        )
        self.assert_no_record()

    # TODO: Add validation and tests for future dates.

    def test_new_post_request_with_blank_company_gets_errors(self):
        # Arrange
        data = {
            "company": "",
            "title": "Some title",
            "interviews": 0,
        }

        # Act
        response = self.client.post(self.test_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationDetails.html")
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1, "There should be one field with errors")
        self.assertFormError(
            form,
            "company",
            "This field is required."
        )
        self.assert_no_record()

    def test_new_post_request_with_blank_title_gets_errors(self):
        # Arrange
        data = {
            "company": "Some company",
            "title": "",
            "interviews": 0,
        }

        # Act
        response = self.client.post(self.test_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationDetails.html")
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1, "There should be one field with errors")
        self.assertFormError(
            form,
            "title",
            "This field is required."
        )
        self.assert_no_record()

    def test_new_post_request_with_minimal_data_gets_no_errors(self):
        # Arrange
        data = {
            "when": "1999-12-31",
            "company": "Some company",
            "title": "Some title",
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
        self.assertEqual(JobApplication.objects.count(), 1)
        record = JobApplication.objects.all()[0]
        self.assertEqual(str(record.when), "1999-12-31")
        self.assertEqual(record.company, "Some company")
        self.assertEqual(record.title, "Some title")
        self.assertEqual(record.posting, None)
        self.assertEqual(record.confirm, None)
        self.assertEqual(record.notes, "")  # Because Django always stores blank TextFields as empty strings.
        self.assertEqual(record.active, False)  # Because a missing checkbox per HTTP means False.
        self.assertEqual(record.rejected, None)
        self.assertEqual(record.interviews, 0)

    def test_new_post_request_with_bad_posting_url_gets_errors(self):
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

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationDetails.html")
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1, "There should only be one field with an error")
        self.assertFormError(
            form,
            "posting",
            "Enter a valid URL."
        )
        self.assert_no_record()

    def test_new_post_request_with_empty_posting_url_gets_no_errors(self):
        # Arrange
        data = {
            "when": "1999-12-31",
            "company": "Some company",
            "title": "Some title",
            "posting": "",
            "active": True,  # Because without a boolean field is the way which HTTP signifies a False value.
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
        self.assertEqual(JobApplication.objects.count(), 1)
        record = JobApplication.objects.all()[0]
        self.assertEqual(str(record.when), "1999-12-31")
        self.assertEqual(record.company, "Some company")
        self.assertEqual(record.title, "Some title")
        self.assertEqual(record.posting, None)
        self.assertEqual(record.confirm, None)
        self.assertEqual(record.notes, "")  # Because Django always stores blank TextFields as empty strings.
        self.assertEqual(record.active, True)
        self.assertEqual(record.rejected, None)
        self.assertEqual(record.interviews, 0)

    def test_new_post_request_with_good_posting_url_gets_no_errors(self):
        # Arrange
        data = {
            "when": "1999-12-31",
            "company": "Some company",
            "title": "Some title",
            "posting": "https://example.com",
            "active": True,  # Because without a boolean field is the way which HTTP signifies a False value.
            "interviews": 1,
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
        self.assertEqual(JobApplication.objects.count(), 1)
        record = JobApplication.objects.all()[0]
        self.assertEqual(str(record.when), "1999-12-31")
        self.assertEqual(record.company, "Some company")
        self.assertEqual(record.title, "Some title")
        self.assertEqual(record.posting, "https://example.com")
        self.assertEqual(record.confirm, None)
        self.assertEqual(record.notes, "")  # Because Django always stores blank TextFields as empty strings.
        self.assertEqual(record.active, True)
        self.assertEqual(record.rejected, None)
        self.assertEqual(record.interviews, 1)

    def test_new_post_request_with_bad_confirm_url_gets_errors(self):
        # Arrange
        data = {
            "when": "1999-12-31",
            "company": "Some company",
            "title": "Some title",
            "confirm": "asdf",
            "interviews": 0,
        }

        # Act
        response = self.client.post(self.test_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationDetails.html")
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1, "There should only be one field with an error")
        self.assertFormError(
            form,
            "confirm",
            "Enter a valid URL."
        )
        self.assert_no_record()

    def test_new_post_request_with_empty_confirm_url_gets_no_errors(self):
        # Arrange
        data = {
            "when": "1999-12-31",
            "company": "Some company",
            "title": "Some title",
            "confirm": "",
            "active": True,  # Because without a boolean field is the way which HTTP signifies a False value.
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
        self.assertEqual(JobApplication.objects.count(), 1)
        record = JobApplication.objects.all()[0]
        self.assertEqual(record.user_id, self.test_user_1.id)
        self.assertEqual(str(record.when), "1999-12-31")
        self.assertEqual(record.company, "Some company")
        self.assertEqual(record.title, "Some title")
        self.assertEqual(record.posting, None)
        self.assertEqual(record.confirm, None)
        self.assertEqual(record.notes, "")  # Due to Django always storing an emtpy string on blank TextField
        self.assertEqual(record.active, True)
        self.assertEqual(record.rejected, None)
        self.assertEqual(record.interviews, 0)

    def test_new_post_request_with_good_confirm_url_gets_no_errors(self):
        # Arrange
        data = {
            "when": "1999-12-31",
            "company": "Some company",
            "title": "Some title",
            "confirm": "https://example.com",
            "active": True,  # Because without a boolean field is the way which HTTP signifies a False value.
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
        self.assertEqual(JobApplication.objects.count(), 1)
        record = JobApplication.objects.all()[0]
        self.assertEqual(str(record.when), "1999-12-31")
        self.assertEqual(record.company, "Some company")
        self.assertEqual(record.title, "Some title")
        self.assertEqual(record.posting, None)
        self.assertEqual(record.confirm, "https://example.com")
        self.assertEqual(record.notes, "")  # Due to Django always storing an emtpy string on blank TextField
        self.assertEqual(record.active, True)
        self.assertEqual(record.rejected, None)
        self.assertEqual(record.interviews, 0)

    def test_new_post_active_true_gets_no_errors(self):
        # Arrange
        data = {
            "when": "1999-12-31",
            "company": "Some company",
            "title": "Some title",
            "active": True,
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
        self.assertEqual(JobApplication.objects.count(), 1)
        record = JobApplication.objects.all()[0]
        self.assertEqual(str(record.when), "1999-12-31")
        self.assertEqual(record.company, "Some company")
        self.assertEqual(record.title, "Some title")
        self.assertEqual(record.posting, None)
        self.assertEqual(record.confirm, None)
        self.assertEqual(record.notes, "")
        self.assertEqual(record.active, True)
        self.assertEqual(record.rejected, None)
        self.assertEqual(record.interviews, 0)

    def test_new_post_active_false_gets_no_errors(self):
        # Arrange - No active field on a checkbox in HTTP means false.
        data = {
            "when": "1999-12-31",
            "company": "Some other company",
            "title": "Some other title",
            "interviews": 0
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
        self.assertEqual(JobApplication.objects.count(), 1)
        record = JobApplication.objects.all()[0]
        self.assertEqual(str(record.when), "1999-12-31")
        self.assertEqual(record.company, "Some other company")
        self.assertEqual(record.title, "Some other title")
        self.assertEqual(record.posting, None)
        self.assertEqual(record.confirm, None)
        self.assertEqual(record.notes, "")
        self.assertEqual(record.active, False)
        self.assertEqual(record.rejected, None)
        self.assertEqual(record.interviews, 0)

    def test_new_post_request_with_bad_rejected_gets_errors(self):
        # Arrange
        data = {
            "when": "1999-12-31",
            "company": "Some company",
            "title": "Some title",
            "rejected": "asdf",
            "interviews": 0,
        }

        # Act
        response = self.client.post(self.test_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationDetails.html")
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1, "There should only be one field with an error")
        self.assertFormError(
            form,
            "rejected",
            "Enter a valid date."
        )
        self.assert_no_record()

    # TODO: Add validation and tests for future dates.

    def test_new_post_request_with_good_rejected_gets_no_errors(self):
        # Arrange
        data = {
            "when": "1999-12-31",
            "company": "Some company",
            "title": "Some title",
            "active": True,  # Because without a boolean field is the way which HTTP signifies a False value.
            "rejected": "2001-01-02",
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
        self.assertEqual(JobApplication.objects.count(), 1)
        record = JobApplication.objects.all()[0]
        self.assertEqual(str(record.when), "1999-12-31")
        self.assertEqual(record.company, "Some company")
        self.assertEqual(record.title, "Some title")
        self.assertEqual(record.posting, None)
        self.assertEqual(record.confirm, None)
        self.assertEqual(record.notes, "")  # Due to Django always storing an emtpy string on blank TextField
        self.assertEqual(record.active, True)
        self.assertEqual(str(record.rejected), "2001-01-02")
        self.assertEqual(record.interviews, 0)

    def test_new_post_request_with_blank_interviews_gets_errors(self):
        # Arrange
        data = {
            "company": "Some company",
            "title": "Some title",
            "interviews": "",
        }

        # Act
        response = self.client.post(self.test_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationDetails.html")
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1, "There should be one field with errors")
        self.assertFormError(
            form,
            "interviews",
            "This field is required."
        )
        self.assert_no_record()

    def test_new_post_request_with_bad_interviews_value_gets_errors(self):
        # Arrange
        data = {
            "when": "1999-12-31",
            "company": "Some company",
            "title": "Some title",
            "interviews": "asdf",
        }

        # Act
        response = self.client.post(self.test_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationDetails.html")
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1, "There should only be one field with an error")
        self.assertFormError(
            form,
            "interviews",
            "Enter a whole number."
        )
        self.assert_no_record()

    def test_new_post_request_with_id_ignores_id_gets_no_errors(self):
        # Arrange
        data = {
            "id": 999,
            "when": "1999-12-31",
            "company": "Some company",
            "title": "Some title",
            "active": True,  # Because without a boolean field is the way which HTTP signifies a False value.
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
        self.assertEqual(JobApplication.objects.count(), 1)
        record = JobApplication.objects.all()[0]
        self.assertNotEqual(record.id, 999)
        self.assertEqual(str(record.when), "1999-12-31")
        self.assertEqual(record.company, "Some company")
        self.assertEqual(record.title, "Some title")
        self.assertEqual(record.posting, None)
        self.assertEqual(record.confirm, None)
        self.assertEqual(record.notes, "")  # Due to Django always storing an emtpy string on blank TextField
        self.assertEqual(record.active, True)
        self.assertEqual(record.rejected, None)
        self.assertEqual(record.interviews, 0)

    def test_new_post_request_with_user_id_ignores_user_id_gets_no_errors(self):
        # Arrange
        data = {
            "user_id": 2,
            "when": "1999-12-31",
            "company": "Some company",
            "title": "Some title",
            "active": True,  # Because without a boolean field is the way which HTTP signifies a False value.
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
        self.assertEqual(JobApplication.objects.count(), 1)
        record = JobApplication.objects.all()[0]
        self.assertEqual(record.user_id, self.test_user_1.id)
        self.assertEqual(str(record.when), "1999-12-31")
        self.assertEqual(record.company, "Some company")
        self.assertEqual(record.title, "Some title")
        self.assertEqual(record.posting, None)
        self.assertEqual(record.confirm, None)
        self.assertEqual(record.notes, "")  # Due to Django always storing an emtpy string on blank TextField
        self.assertEqual(record.active, True)
        self.assertEqual(record.rejected, None)
        self.assertEqual(record.interviews, 0)

    def test_new_post_request_with_both_id_and_user_id_ignores_both_gets_no_errors(self):
        # Arrange
        data = {
            "id": 999,
            "user_id": 2,
            "when": "1999-12-31",
            "company": "Some company",
            "title": "Some title",
            "active": True,  # Because without a boolean field is the way which HTTP signifies a False value.
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
        self.assertEqual(JobApplication.objects.count(), 1)
        record = JobApplication.objects.all()[0]
        self.assertNotEqual(record.id, 999)
        self.assertEqual(record.user_id, self.test_user_1.id)
        self.assertEqual(str(record.when), "1999-12-31")
        self.assertEqual(record.company, "Some company")
        self.assertEqual(record.title, "Some title")
        self.assertEqual(record.posting, None)
        self.assertEqual(record.confirm, None)
        self.assertEqual(record.notes, "")  # Due to Django always storing an emtpy string on blank TextField
        self.assertEqual(record.active, True)
        self.assertEqual(record.rejected, None)
        self.assertEqual(record.interviews, 0)

    def test_new_put_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.put(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 405)

    def test_new_patch_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.patch(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 405)

    def test_new_delete_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.delete(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 405)

    def test_new_head_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.head(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 405)

    def test_new_options_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.options(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 405)


# noinspection DuplicatedCode
class AuthenticatedUserEditApplicationDetailsTests(BaseAuthenticatedUserApplication):
    """
    Test the various submissions of editing job applications, to verify that we see the errors or redirections expected.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_record = JobApplication.objects.create(
            user=cls.test_user_1,
            when="1999-12-31",
            company="Some company",
            title="Some title",
            posting="https://example.com/posting",
            confirm="https://example.com/confirm",
            notes="Some notes",
            active=True,
            rejected="2000-01-02",
            interviews=0,
        )
        cls.test_url = reverse("applications:application-details", kwargs={"appid": cls.test_record.id})
        cls.list_url = reverse("applications:application-list")

    @staticmethod
    def record_to_dict(record: JobApplication, overrides: None | dict[str, Any] = None) -> dict[str, str]:
        """
        Convert a JobApplication into a dictionary, with everything stringified for ease of comparison
        """
        data = {
            "id": str(record.id),
            "user_id": str(record.user_id),
            "when": str(record.when),
            "company": str(record.company),
            "title": str(record.title),
            "posting": str(record.posting),
            "confirm": str(record.confirm),
            "notes": str(record.notes),
            "active": str(record.active),
            "rejected": str(record.rejected),
            "interviews": str(record.interviews),
        }

        if overrides:
            for key, value in overrides.items():
                data[key] = str(value)

        return data

    def assert_expected_form(self, form: EditApplication, data: dict[str, str]):
        self.assertEqual(str(form['when'].value()), str(data['when']))
        self.assertEqual(str(form['company'].value()), str(data['company']))
        self.assertEqual(str(form['title'].value()), str(data['title']))
        self.assertEqual(str(form['posting'].value()), str(data['posting']))
        self.assertEqual(str(form['confirm'].value()), str(data['confirm']))
        self.assertEqual(str(form['notes'].value()), str(data['notes']))
        self.assertEqual(str(form['active'].value()), str(data['active']))
        self.assertEqual(str(form['rejected'].value()), str(data['rejected']))
        self.assertEqual(str(form['interviews'].value()), str(data['interviews']))

    def assert_expected_record(self, data: dict[str, str]):
        """
        Assert that there is still only one record and that it has the expected values.
        """
        self.assertEqual(JobApplication.objects.count(), 1)
        record = JobApplication.objects.all()[0]
        new_dict = self.record_to_dict(record)
        self.assertEqual(new_dict, data)

    def assert_record_unchanged(self):
        """
        Assert that there is only one record and that it is unchanged in the database
        """
        self.assertEqual(JobApplication.objects.count(), 1)
        record = JobApplication.objects.all()[0]
        self.assertEqual(self.test_record, record)

    def test_edit_get_request_gets_edit_application_template(self):
        # Arrange

        # Act
        response = self.client.get(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationDetails.html")
        form = response.context['form']
        self.assert_expected_form(form, self.record_to_dict(self.test_record))

    def test_edit_post_request_with_no_data_gets_errors(self):
        # Arrange
        data = {}

        # Act
        response = self.client.post(self.test_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationDetails.html")
        form = response.context_data["form"]
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
        self.assertEqual(str(form['when'].value()), 'None')
        self.assertEqual(form['company'].value(), None)
        self.assertEqual(form['title'].value(), None)
        self.assertEqual(form['posting'].value(), None)
        self.assertEqual(form['confirm'].value(), None)
        self.assertEqual(form['notes'].value(), None)
        self.assertEqual(form['active'].value(), False)
        self.assertEqual(form['rejected'].value(), None)
        self.assertEqual(form['interviews'].value(), None)

    def test_edit_post_request_with_bad_when_gets_errors(self):
        # Arrange
        data = {
            "when": "asdf",
            "company": self.test_record.company,
            "title": self.test_record.title,
            "posting": self.test_record.posting,
            "confirm": self.test_record.confirm,
            "notes": self.test_record.notes,
            "active": self.test_record.active,
            "rejected": self.test_record.rejected,
            "interviews": self.test_record.interviews,
        }

        # Act
        response = self.client.post(self.test_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationDetails.html")
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1, "There should only be one field with an error")
        self.assertFormError(
            form,
            "when",
            "Enter a valid date."
        )
        self.assert_expected_form(form, data)
        self.assert_record_unchanged()

    # TODO: Add validation and tests for future dates.

    def test_edit_post_request_with_blank_company_gets_errors(self):
        # Arrange
        data = {
            "when": self.test_record.when,
            "company": "",
            "title": self.test_record.title,
            "posting": self.test_record.posting,
            "confirm": self.test_record.confirm,
            "notes": self.test_record.notes,
            "active": self.test_record.active,
            "rejected": self.test_record.rejected,
            "interviews": self.test_record.interviews,
        }

        # Act
        response = self.client.post(self.test_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationDetails.html")
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1, "There should be one field with errors")
        self.assertFormError(
            form,
            "company",
            "This field is required."
        )
        self.assert_expected_form(form, data)
        self.assert_record_unchanged()

    def test_edit_post_request_with_blank_title_gets_errors(self):
        # Arrange
        data = {
            "when": self.test_record.when,
            "company": self.test_record.company,
            "title": "",
            "posting": self.test_record.posting,
            "confirm": self.test_record.confirm,
            "notes": self.test_record.notes,
            "active": self.test_record.active,
            "rejected": self.test_record.rejected,
            "interviews": self.test_record.interviews,
        }

        # Act
        response = self.client.post(self.test_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationDetails.html")
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1, "There should be one field with errors")
        self.assertFormError(
            form,
            "title",
            "This field is required."
        )
        self.assert_expected_form(form, data)
        self.assert_record_unchanged()

    def test_edit_post_request_with_bad_posting_url_gets_errors(self):
        # Arrange
        data = {
            "when": self.test_record.when,
            "company": self.test_record.company,
            "title": self.test_record.title,
            "posting": "asdf",
            "confirm": self.test_record.confirm,
            "notes": self.test_record.notes,
            "active": self.test_record.active,
            "rejected": self.test_record.rejected,
            "interviews": self.test_record.interviews,
        }

        # Act
        response = self.client.post(self.test_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationDetails.html")
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1, "There should only be one field with an error")
        self.assertFormError(
            form,
            "posting",
            "Enter a valid URL."
        )
        self.assert_expected_form(form, data)
        self.assert_record_unchanged()

    def test_edit_post_request_with_empty_posting_url_gets_no_errors(self):
        # Arrange
        data = {
            "when": self.test_record.when,
            "company": self.test_record.company,
            "title": self.test_record.title,
            "posting": "",
            "confirm": self.test_record.confirm,
            "notes": self.test_record.notes,
            "active": self.test_record.active,
            "rejected": self.test_record.rejected,
            "interviews": self.test_record.interviews,
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
        self.assert_expected_record(self.record_to_dict(self.test_record, {"posting": None}))

    def test_edit_post_request_with_good_posting_url_gets_no_errors(self):
        # Arrange
        data = {
            "when": self.test_record.when,
            "company": self.test_record.company,
            "title": self.test_record.title,
            "posting": "https://example.com/some-other-posting",
            "confirm": self.test_record.confirm,
            "notes": self.test_record.notes,
            "active": self.test_record.active,
            "rejected": self.test_record.rejected,
            "interviews": self.test_record.interviews,
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
        self.assert_expected_record(
            self.record_to_dict(self.test_record, {"posting": "https://example.com/some-other-posting"}))

    def test_edit_post_request_with_bad_confirm_url_gets_errors(self):
        # Arrange
        data = {
            "when": self.test_record.when,
            "company": self.test_record.company,
            "title": self.test_record.title,
            "posting": self.test_record.posting,
            "confirm": "asdf",
            "notes": self.test_record.notes,
            "active": self.test_record.active,
            "rejected": self.test_record.rejected,
            "interviews": self.test_record.interviews,
        }

        # Act
        response = self.client.post(self.test_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationDetails.html")
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1, "There should only be one field with an error")
        self.assertFormError(
            form,
            "confirm",
            "Enter a valid URL."
        )
        self.assert_expected_form(form, data)
        self.assert_record_unchanged()

    def test_edit_post_request_with_empty_confirm_url_gets_no_errors(self):
        # Arrange
        data = {
            "when": self.test_record.when,
            "company": self.test_record.company,
            "title": self.test_record.title,
            "posting": self.test_record.posting,
            "confirm": "",
            "notes": self.test_record.notes,
            "active": self.test_record.active,
            "rejected": self.test_record.rejected,
            "interviews": self.test_record.interviews,
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
        self.assert_expected_record(self.record_to_dict(self.test_record, {"confirm": None}))

    def test_edit_post_request_with_good_confirm_url_gets_no_errors(self):
        # Arrange
        data = {
            "when": self.test_record.when,
            "company": self.test_record.company,
            "title": self.test_record.title,
            "posting": self.test_record.posting,
            "confirm": "https://example.com/some-other-confirm",
            "notes": self.test_record.notes,
            "active": self.test_record.active,
            "rejected": self.test_record.rejected,
            "interviews": self.test_record.interviews,
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
        self.assert_expected_record(
            self.record_to_dict(self.test_record, {"confirm": "https://example.com/some-other-confirm"}))

    def test_edit_post_active_true_gets_no_errors(self):
        # Arrange
        data = {
            "when": self.test_record.when,
            "company": self.test_record.company,
            "title": self.test_record.title,
            "posting": self.test_record.posting,
            "confirm": self.test_record.confirm,
            "notes": self.test_record.notes,
            "active": True,
            "rejected": self.test_record.rejected,
            "interviews": self.test_record.interviews,
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
        self.assert_expected_record(self.record_to_dict(self.test_record, {"active": True}))

    def test_edit_post_active_false_gets_no_errors(self):
        # Arrange
        data = {
            "when": self.test_record.when,
            "company": self.test_record.company,
            "title": self.test_record.title,
            "posting": self.test_record.posting,
            "confirm": self.test_record.confirm,
            "notes": self.test_record.notes,
            "active": False,
            "rejected": self.test_record.rejected,
            "interviews": self.test_record.interviews,
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
        self.assert_expected_record(self.record_to_dict(self.test_record, {"active": False}))

    def test_edit_post_request_with_bad_rejected_gets_errors(self):
        # Arrange
        data = {
            "when": self.test_record.when,
            "company": self.test_record.company,
            "title": self.test_record.title,
            "posting": self.test_record.posting,
            "confirm": self.test_record.confirm,
            "notes": self.test_record.notes,
            "active": self.test_record.active,
            "rejected": "asdf",
            "interviews": self.test_record.interviews,
        }

        # Act
        response = self.client.post(self.test_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationDetails.html")
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1, "There should only be one field with an error")
        self.assertFormError(
            form,
            "rejected",
            "Enter a valid date."
        )
        self.assert_expected_form(form, data)
        self.assert_record_unchanged()

    # TODO: Add validation and tests for future dates.

    def test_edit_post_request_with_good_rejected_gets_no_errors(self):
        # Arrange
        data = {
            "when": self.test_record.when,
            "company": self.test_record.company,
            "title": self.test_record.title,
            "posting": self.test_record.posting,
            "confirm": self.test_record.confirm,
            "notes": self.test_record.notes,
            "active": self.test_record.active,
            "rejected": "2025-01-02",
            "interviews": self.test_record.interviews,
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
        self.assert_expected_record(self.record_to_dict(self.test_record, {"rejected": "2025-01-02"}))

    def test_edit_post_request_with_blank_interviews_gets_errors(self):
        # Arrange
        data = {
            "when": self.test_record.when,
            "company": self.test_record.company,
            "title": self.test_record.title,
            "posting": self.test_record.posting,
            "confirm": self.test_record.confirm,
            "notes": self.test_record.notes,
            "active": self.test_record.active,
            "rejected": self.test_record.rejected,
            "interviews": "",
        }

        # Act
        response = self.client.post(self.test_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationDetails.html")
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1, "There should be one field with errors")
        self.assertFormError(
            form,
            "interviews",
            "This field is required."
        )
        self.assert_expected_form(form, data)
        self.assert_record_unchanged()

    def test_edit_post_request_with_bad_interviews_value_gets_errors(self):
        # Arrange
        data = {
            "when": self.test_record.when,
            "company": self.test_record.company,
            "title": self.test_record.title,
            "posting": self.test_record.posting,
            "confirm": self.test_record.confirm,
            "notes": self.test_record.notes,
            "active": self.test_record.active,
            "rejected": self.test_record.rejected,
            "interviews": "asdf",
        }

        # Act
        response = self.client.post(self.test_url, data)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ApplicationDetails.html")
        form = response.context_data["form"]
        self.assertEqual(len(form.errors), 1, "There should only be one field with an error")
        self.assertFormError(
            form,
            "interviews",
            "Enter a whole number."
        )
        self.assert_expected_form(form, data)
        self.assert_record_unchanged()

    def test_edit_get_request_invalid_user_id_gets_404_error(self):
        """
        Here, we are testing specifically to make sure that a user cannot get a record which does not belong to them,
        and that an error is logged.
        """
        # Arrange
        client = Client()
        client.force_login(self.test_user_2)

        # Act
        with self.assertLogs("applications.views", level="WARNING") as cm:
            response = client.get(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertIn(
            f"WARNING:applications.views:Http404 raised in ApplicationDetails by testuser2 (id={self.test_user_2.id}) on id={self.test_record.id}: No job application found matching the query",
            cm.output
        )

    def test_edit_post_request_attempt_implicit_user_id_override_fails(self):
        """
        Here, we are testing to make sure that a user cannot maliciously overwrite the record of another user, and
        instead gets a 404 error, which is also logged.
        """
        # Arrange
        data = {
            "when": self.test_record.when,
            "company": self.test_record.company,
            "title": self.test_record.title,
            "posting": self.test_record.posting,
            "confirm": self.test_record.confirm,
            "notes": self.test_record.notes,
            "active": self.test_record.active,
            "rejected": self.test_record.rejected,
            "interviews": self.test_record.interviews,
        }
        client = Client()
        client.force_login(self.test_user_2)

        # Act
        with self.assertLogs("applications.views", level="WARNING") as cm:
            response = client.post(self.test_url, data)

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertIn(
            f"WARNING:applications.views:Http404 raised in ApplicationDetails by testuser2 (id={self.test_user_2.id}) on id={self.test_record.id}: No job application found matching the query",
            cm.output
        )
        self.assert_record_unchanged()

    def test_edit_post_request_attempt_explicit_user_id_override_fails(self):
        """
        Here, we are testing to make sure that a user cannot maliciously overwrite the record of another user by
        explicitly specifying the user_id on a record belonging to another user, and instead gets a 404 error, which is
        also logged.
        """
        # Arrange
        data = {
            "user_id": 2,
            "when": self.test_record.when,
            "company": self.test_record.company,
            "title": self.test_record.title,
            "posting": self.test_record.posting,
            "confirm": self.test_record.confirm,
            "notes": self.test_record.notes,
            "active": self.test_record.active,
            "rejected": self.test_record.rejected,
            "interviews": "asdf",
        }
        client = Client()
        client.force_login(self.test_user_2)

        # Act
        with self.assertLogs("applications.views", level="WARNING") as cm:
            response = client.post(self.test_url, data)

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertIn(
            f"WARNING:applications.views:Http404 raised in ApplicationDetails by testuser2 (id={self.test_user_2.id}) on id={self.test_record.id}: No job application found matching the query",
            cm.output
        )
        self.assert_record_unchanged()

    def test_edit_post_request_attempt_explicit_id_and_user_id_override_fails(self):
        """
        Here, we are testing to make sure that a user cannot maliciously attempt to save a bogus record with both the
        id and user_id specified. The user should get a HTTP 404 error and the fact should be logged.
        """
        # Arrange
        data = {
            "id": 99,
            "user_id": 2,
            "when": self.test_record.when,
            "company": self.test_record.company,
            "title": self.test_record.title,
            "posting": self.test_record.posting,
            "confirm": self.test_record.confirm,
            "notes": self.test_record.notes,
            "active": self.test_record.active,
            "rejected": self.test_record.rejected,
            "interviews": "asdf",
        }
        client = Client()
        client.force_login(self.test_user_2)

        # Act
        with self.assertLogs("applications.views", level="WARNING") as cm:
            response = client.post(reverse("applications:application-details", kwargs={"appid": 99}), data)

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertIn(
            f"WARNING:applications.views:Http404 raised in ApplicationDetails by testuser2 (id={self.test_user_2.id}) on id=99: No job application found matching the query",
            cm.output
        )
        self.assert_record_unchanged()

    def test_edit_put_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.put(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 405)

    def test_edit_patch_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.patch(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 405)

    def test_edit_delete_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.delete(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 405)

    def test_edit_head_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.head(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 405)

    def test_edit_options_request_gets_an_error(self):
        # Arrange

        # Act
        response = self.client.options(self.test_url)

        # Assert
        self.assertEqual(response.status_code, 405)


if __name__ == "__main__":
    unittest.main()
