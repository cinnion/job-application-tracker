"""
These are tests which deal with authenticated user requests for the URLs associated with this package.
"""

import json
import os
import time
from typing import TypeVar

from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from applications.models import JobApplication

# Define a generic type
T = TypeVar("T", bound=models.Model)


# noinspection DuplicatedCode - While the body is the same as BaseAuthenticatedUserApplication, the parent is different.
class BaseAuthenticatedUserApplicationApi(APITestCase):
    """
    These methods are common to all the tests with an authenticated user client.
    """
    test_user_1: AbstractBaseUser
    test_user_2: AbstractBaseUser
    test_user_3: AbstractBaseUser

    @classmethod
    def loadFixtureData(cls, model_class: type[T], datafile: str) -> list[T]:
        """
        Load the data from a fixture data file, bulk insert, and return the resulting objects.
        """

        # Load the record data
        datafile = os.path.join(os.path.dirname(os.path.abspath(__file__)), datafile)
        with open(datafile, "r") as file:
            data = json.load(file)

        # Build our set of unsaved records
        records = [
            model_class(**{
                **record["fields"],
                "user": getattr(cls, f"test_user_{record["fields"]["user"]}")
            }) if model_class.__name__ == "JobApplication"
            else model_class(**record["fields"])
            for record in data
        ]

        # Now do a bulk create of the records
        model_class.objects.bulk_create(records, batch_size=None, ignore_conflicts=False)

        # Return the database records
        return records

    @classmethod
    def setUpTestData(cls):
        """
        Create our test users and load our test data
        """
        super().setUpTestData()

        start = time.perf_counter_ns()

        # Get our user model
        user_model = get_user_model()

        # Load our test users from the user fixture data file
        users = cls.loadFixtureData(user_model, "fixtures/users.json")

        # Save the users as class attributes
        for index, value in enumerate(users):
            setattr(cls, f"test_user_{index+1}", value)

        # Load our data for the job applications
        cls.records = cls.loadFixtureData(JobApplication, "fixtures/job_applications.json")

        end = time.perf_counter_ns()
        print(f"Data has been loaded - it took {(end - start) / 1_000_000_000} seconds to load {len(users)} users and {len(cls.records)} job applications.")

    def setUp(self):
        """
        Create our authenticated client for use by the individual tests.
        """
        self.client = self.client_class()
        self.client.force_login(self.test_user_1)


class AuthenticatedUserApplicationApiTests(BaseAuthenticatedUserApplicationApi):

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

    def test_get_application_list_with_query_data(self):
        # Arrange
        client = self.client_class()
        client.force_login(self.test_user_2)

        expected_data = {
            "status": "success",
            "draw": 3,
            "recordsTotal": 200,
            "recordsFiltered": 200,
            "job_applications": [
                {
                    "id": u.id,
                    "when": u.when,
                    "company": u.company,
                    "title": u.title,
                    "posting": u.posting,
                    "confirm": u.confirm,
                    "notes": u.notes,
                    "active": u.active,
                    "interviews": u.interviews,
                    "rejected": u.rejected,
                    "created_at": u.created_at.astimezone().isoformat(),
                    "updated_at": u.updated_at.astimezone().isoformat(),
                    "user": u.user_id,
                }
                for u in self.records[0:10] if u.user_id == self.test_user_2.id
            ]
        }
        query_data = {
            "draw": 3,
        }
        test_url = reverse("applications-api:applications-list", query=query_data)

        # Act
        response = client.get(test_url, format="json")

        # Assert
        self.maxDiff = None
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
