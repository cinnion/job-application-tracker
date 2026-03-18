import datetime
from unittest import mock

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import timezone

from applications.models import JobApplication


class JobApplicationTestCase(TestCase):
    def test_job_when_field_cannot_be_blank(self):
        # Arrange

        # Act
        with self.assertRaises(ValidationError) as cm:
            JobApplication.objects.create(
                when="",
                company="Some company",
                title="Some title",
                posting="https://posting.example.com",
                confirm="https://confirm.example.com",
                notes="Some notes",
                rejected="1999-12-31"
            )

        # Assert
        self.assertEqual(cm.exception.message, '“%(value)s” value has an invalid date format. It must be in YYYY-MM-DD format.')

    def test_job_when_field_cannot_be_non_date(self):
        # Arrange
        obj = JobApplication(
            when="asdf",
            company="Some company",
            title="Some title",
            posting="https://posting.example.com",
            confirm="https://confirm.example.com",
            notes="Some notes",
            rejected="1999-12-31"
        )

        # Act
        with self.assertRaises(ValidationError) as cm:
            obj.full_clean()

        self.assertEqual(cm.exception.messages, ['“asdf” value has an invalid date format. It must be in YYYY-MM-DD format.'])

    def test_job_company_field_cannot_be_blank(self):
        # Arrange
        obj = JobApplication(
            when="1999-12-31",
            company="",
            title="Some title",
            posting="https://posting.example.com",
            confirm="https://confirm.example.com",
            notes="Some notes",
            rejected="1999-12-31"
        )

        # Act
        with self.assertRaises(ValidationError) as cm:
            obj.full_clean()

        self.assertEqual(cm.exception.messages, ['This field cannot be blank.'])

    def test_job_title_field_cannot_be_null(self):
        # Arrange

        # Act
        with self.assertRaises(IntegrityError) as cm:
            JobApplication.objects.create(
                when="1999-12-31",
                company="Some company",
                title=None,
                posting="https://posting.example.com",
                confirm="https://confirm.example.com",
                notes="Some notes",
                rejected="1999-12-31"
            )

        # Assert
        self.assertIn('null value in column "title" of relation "job_applications" violates not-null constraint', cm.exception.args[0])

    def test_job_title_field_can_be_blank(self):
        # Arrange
        obj = JobApplication.objects.create(
            when="1999-12-31",
            company="Some company",
            title="",
            posting="https://posting.example.com",
            confirm="https://confirm.example.com",
            notes="Some notes",
            rejected="1999-12-31"
        )

        # Act
        try:
            obj.full_clean()
        except ValidationError:
            self.fail("Title field with blank string raised ValidationError when it should not.")

    def test_job_posting_field_cannot_be_null(self):
        # Arrange

        # Act
        with self.assertRaises(IntegrityError) as cm:
            JobApplication.objects.create(
                when="1999-12-31",
                company="Some company",
                title="",
                posting=None,
                confirm="https://confirm.example.com",
                notes="Some notes",
                rejected="1999-12-31"
            )

        # Assert
        self.assertIn('null value in column "posting" of relation "job_applications" violates not-null constraint', cm.exception.args[0])

    def test_job_posting_field_can_be_blank(self):
        # Arrange
        obj = JobApplication.objects.create(
            when="1999-12-31",
            company="Some company",
            title="",
            posting="",
            confirm="https://confirm.example.com",
            notes="Some notes",
            rejected="1999-12-31"
        )

        # Act
        try:
            obj.full_clean()
        except ValidationError:
            self.fail("Posting field with blank string raised ValidationError when it should not.")

    def test_job_posting_field_cannot_be_non_url(self):
        # Arrange Create the object with "asdf" for the posting field.
        obj = JobApplication(
            when="1999-12-31",
            company="Some company",
            title="Some title",
            posting="asdf",
            confirm="https://confirm.example.com",
            notes="Some notes",
            rejected="1999-12-31"
        )

        # Act
        with self.assertRaises(ValidationError) as cm:
            obj.full_clean()

        self.assertEqual(cm.exception.messages, ['Enter a valid URL.'])

    def test_job_with_no_title_has_blank_title(self):
        # Arrange
        obj = JobApplication.objects.create(
            when="1999-12-31",
            company="some company",
            confirm="",
            posting="",
            notes="Some notes...",
            active=True,
        )

        # Act
        obj.refresh_from_db()

        # Assert
        self.assertEqual(obj.title, "")

    def test_job_confirm_field_cannot_be_null(self):
        # Arrange

        # Act
        with self.assertRaises(IntegrityError) as cm:
            JobApplication.objects.create(
                when="1999-12-31",
                company="Some company",
                title="",
                posting="",
                confirm=None,
                notes="Some notes",
                rejected="1999-12-31"
            )

        # Assert
        self.assertIn('null value in column "confirm" of relation "job_applications" violates not-null constraint', cm.exception.args[0])

    def test_job_confirm_field_can_be_blank(self):
        # Arrange
        obj = JobApplication.objects.create(
            when="1999-12-31",
            company="Some company",
            title="",
            posting="",
            confirm="",
            notes="Some notes",
            rejected="1999-12-31"
        )

        # Act
        try:
            obj.full_clean()
        except ValidationError:
            self.fail("Confirm field with blank string raised ValidationError when it should not.")

    def test_job_confirm_field_cannot_be_non_url(self):
        # Arrange
        obj = JobApplication(
            when="1999-12-31",
            company="Some company",
            title="Some title",
            posting="",
            confirm="asdf",
            notes="Some notes",
            rejected="1999-12-31"
        )

        # Act
        with self.assertRaises(ValidationError) as cm:
            obj.full_clean()

        self.assertEqual(cm.exception.messages, ['Enter a valid URL.'])

    def test_job_with_no_confirm_has_blank_confirm(self):
        # Arrange
        obj = JobApplication.objects.create(
            when="1999-12-31",
            company="some company",
            title="",
            posting="",
            notes="Some notes...",
            active=True,
        )

        # Act
        obj.refresh_from_db()

        # Assert
        self.assertEqual(obj.confirm, "")

    def test_job_notes_field_cannot_be_null(self):
        # Arrange

        # Act
        with self.assertRaises(IntegrityError) as cm:
            JobApplication.objects.create(
                when="1999-12-31",
                company="Some company",
                title="",
                posting="",
                confirm="",
                notes=None,
                rejected="1999-12-31"
            )

        # Assert
        self.assertIn('null value in column "notes" of relation "job_applications" violates not-null constraint', cm.exception.args[0])

    def test_job_notes_field_can_be_blank(self):
        # Arrange
        obj = JobApplication.objects.create(
            when="1999-12-31",
            company="Some company",
            title="",
            posting="",
            confirm="",
            notes="",
            rejected="1999-12-31"
        )

        # Act
        try:
            obj.full_clean()
        except ValidationError:
            self.fail("Notes field with blank string raised ValidationError when it should not.")

    def test_job_with_no_notes_has_blank_notes(self):
        # Arrange
        obj = JobApplication.objects.create(
            when="1999-12-31",
            company="some company",
            title="",
            posting="",
            confirm="",
            active=True,
        )

        # Act
        obj.refresh_from_db()

        # Assert
        self.assertEqual(obj.notes, "")

    def test_job_with_no_active_has_true_default(self):
        # Arrange
        obj = JobApplication.objects.create(
            when="1999-12-31",
            company="some company",
            title="",
            posting="",
            confirm="",
            rejected=None,
        )

        # Act
        obj.refresh_from_db()

        # Assert
        self.assertTrue(obj.active)

    def test_job_with_true_active_has_true(self):
        # Arrange
        obj = JobApplication.objects.create(
            when="1999-12-31",
            company="some company",
            title="",
            posting="",
            confirm="",
            active=True,
            rejected=None,
        )

        # Act
        obj.refresh_from_db()

        # Assert
        self.assertTrue(obj.active)

    def test_job_with_false_active_has_false(self):
        # Arrange
        obj = JobApplication.objects.create(
            when="1999-12-31",
            company="some company",
            title="",
            posting="",
            confirm="",
            active=False,
            rejected=None,
        )

        # Act
        obj.refresh_from_db()

        # Assert
        self.assertFalse(obj.active)

    def test_job_with_blank_active_gets_validation_error(self):
        # Arrange
        obj = JobApplication(
            when="1999-12-31",
            company="some company",
            title="",
            posting="",
            confirm="",
            active="",
            rejected=None,
        )

        # Act
        with self.assertRaises(ValidationError) as cm:
            obj.full_clean()

        # Assert
        self.assertEqual(cm.exception.messages, ['“” value must be either True or False.'])

    def test_job_unspecified_rejected_field_defaults_null(self):
        # Arrange

        # Act
        try:
            obj = JobApplication.objects.create(
                when="1999-12-31",
                company="Some company",
                title="Some title",
                posting="",
                confirm="",
                notes="",
            )
        except ValidationError:
            self.fail('Rejected field of none raised ValidationError when it should not.')
        except IntegrityError:
            self.fail('Rejected field of none raised database error when it should not.')

        obj.refresh_from_db()

        # Assert
        self.assertIsNone(obj.rejected)

    def test_job_rejected_field_can_be_none_defaults_null(self):
        # Arrange

        # Act
        try:
            obj = JobApplication.objects.create(
                when="1999-12-31",
                company="Some company",
                title="Some title",
                posting="",
                confirm="",
                notes="",
                rejected=None
            )
        except ValidationError:
            self.fail('Rejected field of none raised ValidationError when it should not.')
        except IntegrityError:
            self.fail('Rejected field of none raised database error when it should not.')

        obj.refresh_from_db()

        # Assert
        self.assertIsNone(obj.rejected)

    def test_job_rejected_field_blank_defaults_null(self):
        # Arrange

        # Act
        with self.assertRaises(ValidationError) as cm:
            JobApplication.objects.create(
                when="1999-12-31",
                company="Some company",
                title="Some title",
                posting="",
                confirm="",
                notes="",
                rejected=""
            )

        # Assert
        self.assertEqual(cm.exception.message, '“%(value)s” value has an invalid date format. It must be in YYYY-MM-DD format.')

    def test_job_rejected_field_cannot_be_non_date(self):
        # Arrange
        obj = JobApplication(
            when="1999-12-31",
            company="Some company",
            title="Some title",
            posting="https://posting.example.com",
            confirm="https://confirm.example.com",
            notes="Some notes",
            rejected="asdf"
        )

        # Act
        with self.assertRaises(ValidationError) as cm:
            obj.full_clean()

        self.assertEqual(cm.exception.messages, ['“asdf” value has an invalid date format. It must be in YYYY-MM-DD format.'])

    def test_job_created_at_field_defaults_to_now(self):
        # Arrange
        mocked = datetime.datetime(2020, 1, 31, 2, 4, 6, tzinfo=datetime.timezone.utc)

        # Act
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked)):
            obj = JobApplication.objects.create(
                when="1999-12-31",
                company="Some company",
                title="Some title",
                posting="https://posting.example.com",
                confirm="https://confirm.example.com",
                notes="Some notes",
                rejected="1999-12-31"
            )

        obj.refresh_from_db()

        # Assert
        self.assertEqual(obj.created_at, mocked)

    def test_job_created_at_field_in_past_ignores_override_and_uses_now(self):
        # Arrange
        mocked = timezone.make_aware(datetime.datetime(2020, 1, 31, 2, 4, 6))
        past_time = timezone.make_aware(datetime.datetime(1999, 1, 31, 2, 4, 6))

        # Act
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked)):
            obj = JobApplication.objects.create(
                when="1999-12-31",
                company="Some company",
                title="Some title",
                posting="https://posting.example.com",
                confirm="https://confirm.example.com",
                notes="Some notes",
                rejected="1999-12-31",
                created_at=past_time.__str__()
            )

        obj.refresh_from_db()

        # Assert
        self.assertEqual(obj.created_at, mocked)

    def test_job_updated_at_field_defaults_to_now(self):
        # Arrange
        mocked = datetime.datetime(2020, 1, 31, 2, 4, 6, tzinfo=datetime.timezone.utc)

        # Act
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked)):
            obj = JobApplication.objects.create(
                when="1999-12-31",
                company="Some company",
                title="Some title",
                posting="https://posting.example.com",
                confirm="https://confirm.example.com",
                notes="Some notes",
                rejected="1999-12-31"
            )

        obj.refresh_from_db()

        # Assert
        self.assertEqual(obj.updated_at, mocked)

    def test_job_updated_at_field_in_past_ignores_override_and_uses_now(self):
        # Arrange
        mocked = timezone.make_aware(datetime.datetime(2020, 1, 31, 2, 4, 6))
        past_time = timezone.make_aware(datetime.datetime(1999, 1, 31, 2, 4, 6))

        # Act
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked)):
            obj = JobApplication.objects.create(
                when="1999-12-31",
                company="Some company",
                title="Some title",
                posting="https://posting.example.com",
                confirm="https://confirm.example.com",
                notes="Some notes",
                rejected="1999-12-31",
                updated_at=past_time.__str__()
            )

        obj.refresh_from_db()

        # Assert
        self.assertEqual(obj.updated_at, mocked)

    def test_job_string_formats_properly(self):
        # Arrange
        obj = JobApplication(
            when="1999-12-31",
            title="Some title",
            company="Some company"
        )

        # Act
        result = obj.__str__()

        # Assert
        self.assertEqual(result, '1999-12-31: Some title @ Some company')
