"""
These are tests which deal with authenticated user requests for the URLs associated with this package.
"""

from django.db.models import QuerySet
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from applications.models import JobApplication
from core.tests.mixins import (
    BaseAuthenticatedUserMixin,
    DataTableTestMixin,
    SortingCriteria,
    DataTableColumn
)


# noinspection DuplicatedCode
class AuthenticatedUserJobApplicationsApiTests(BaseAuthenticatedUserMixin, APITestCase, DataTableTestMixin):
    api_url = "applications-api:applications-list"
    deferred_fixtures = ["fixtures/job_applications.json"]

    # @formatter:off
    columns = [
        #               data       name        Searchable  Orderable   Value   Regex
        DataTableColumn("",        "",         True,       False,      "",     False),
        DataTableColumn("id",      "id",       False,      True,       "",     False),
        DataTableColumn("when",    "when",     True,       True,       "",     False),
        DataTableColumn("company", "company",  True,       True,       "",     False),
        DataTableColumn("title",   "title",    True,       True,       "",     False),
        DataTableColumn("posting", "posting",  True,       True,       "",     False),
        DataTableColumn("confirm", "confirm",  True,       True,       "",     False),
        DataTableColumn("notes",   "notes",    True,       True,       "",     False),
        DataTableColumn("active",  "active",   True,       True,       "",     False),
        DataTableColumn("9",       "edit",     True,       True,       "",     False),
    ]
    # @formatter:on

    maxDiff = None

    model = JobApplication

    @staticmethod
    def transform_record_into_dict(record: JobApplication) -> dict:
        """
        Create a dictionary of values from a JobApplication record for conversion to a JSON data row.

        This is used to build up an expected response data structure for validating the response from the view.
        """
        return {
            "id": record.id,
            "when": str(record.when),
            "company": record.company,
            "title": record.title,
            "posting": record.posting,
            "confirm": record.confirm,
            "notes": record.notes,
            "active": record.active,
            "interviews": record.interviews,
            "rejected": record.rejected,
            "created_at": record.created_at.astimezone().isoformat(),
            "updated_at": record.updated_at.astimezone().isoformat(),
            "user": record.user_id,
        }

    @classmethod
    def setUpClass(cls):
        """
        Set up our common test_url.
        """
        super().setUpClass()
        cls.test_url = reverse("applications-api:applications-list")

    def test_get_application_list_no_data(self):
        # Arrange
        expected_data = {
            "status": "success",
            "draw": 1,
            "recordsTotal": 0,
            "recordsFiltered": 0,
            "job_applications": []
        }

        # Act
        response = self.client.get(self.test_url, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(response.data, expected_data)

    def test_get_list_with_start_length_query_data_returns_correct_data(self):
        # Arrange
        client, expected_data, test_url = self.get_test_arrangement(
            user=self.test_user_3,
            draw=3,
            start=25,
            length=25
        )

        # Act
        response = client.get(test_url, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/json")
        del response.data["job_applications"].serializer
        response.data["job_applications"] = list(response.data["job_applications"])
        self.assertEqual(response.data, expected_data)

    def test_get_list_with_search_query_data_returns_correct_data(self):
        # Arrange
        def filter_func(qs: QuerySet) -> QuerySet:
            return qs.filter(company__icontains="Micro")

        client, expected_data, test_url = self.get_test_arrangement(
            user=self.test_user_3,
            draw=4,
            start=10,
            length=10,
            filter_func=filter_func,
            search="Micro"
        )

        # Act
        response = client.get(test_url, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/json")
        del response.data["job_applications"].serializer
        response.data["job_applications"] = list(response.data["job_applications"])
        self.assertEqual(response.data, expected_data)

    def test_get_list_with_search_query_data_returns_correct_data2(self):
        # Arrange
        client, expected_data, test_url = self.get_test_arrangement(
            user=self.test_user_3,
            draw=5,
            start=0,
            length=25,
            order=[
                SortingCriteria(1, "desc", "id"),
                SortingCriteria(4, "desc", "title"),
                SortingCriteria(2, "desc", "when"),
            ],
            order_by=["-id", "-title", "-when"]
        )

        # Act
        response = client.get(test_url, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/json")
        del response.data["job_applications"].serializer
        response.data["job_applications"] = list(response.data["job_applications"])
        self.assertEqual(response.data, expected_data)

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

        # print(f"expected_data = {json.dumps(expected_data, indent=4)}")
        # print(f"response_data = {json.dumps(response.data, indent=4)}")
