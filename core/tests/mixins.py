"""
This is a set of mixins for testing the server-side AJAX calls made by a DataTable instance.
"""
import os
import time
from itertools import tee
from pathlib import Path
from typing import Callable, NamedTuple

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.core import serializers
from django.core.management import CommandParser
from django.db.models import QuerySet
from django.test.client import Client as DjangoClient
from django.test.testcases import SimpleTestCase
from django.urls import reverse


# Define a named tuple for sorting criteria
class SortingCriteria(NamedTuple):
    column: int
    ascdesc: str
    name: str


# noinspection DuplicatedCode - While the body is the same as BaseAuthenticatedUserApplication, the parent is different.
class BaseAuthenticatedUserMixin:
    """
    These methods are common to all the tests with an authenticated user client.
    """
    verbosity: int = 0
    deferred_fixtures = []
    fixture_search_dirs = [
        "core/tests",
        settings.BASE_DIR,
    ]

    def __init_subclass__(cls, **kwargs):
        """
        Initialize fixtures if needed and inject core/tests/fixtures/users.json into the list if it is not already
        there.

        The noinspection comments is because PyCharm is getting confused trying to follow all the types we are
        messing with, and we cannot combine them on the method successfully.
        """
        super().__init_subclass__(**kwargs)

        # noinspection PyUnresolvedReferences
        if cls.fixtures is None:
            cls.fixtures = []
        if "core/tests/fixtures/users.json" not in cls.fixtures:
            cls.fixtures.insert(0, "core/tests/fixtures/users.json")

        # noinspection PyArgumentList
        cls.fixture_search_dirs.insert(0, os.path.join(*cls.__module__.rsplit(".")[:-1]))

    @classmethod
    def setup_verbosity(cls):
        """
        Set our verbosity attribute so that we can conditionally output certain bits of information based on the
        verbosity the test is being run.
        """
        parser = CommandParser(exit_on_error=False)

        parser.add_argument(
            "-v",
            "--verbosity",
            action="store",
            default=1,
            type=int,
            choices=[0, 1, 2, 3],
        )

        parser.parse_known_args(namespace=cls)

    @classmethod
    def loadFixtureData(cls, datafile: str) -> int:
        """
        Load the data from a fixture data file, bulk insert, and return the resulting objects. It is assumed the
        data file consists of only a single type of data, which is why we injected the user.json file into the fixtures
        attribute the way we did in __init_subclass__, since it contains both users and groups, but is small enough
        that calling the loaddata command is not a big hit.

        The noinspection comments are because PyCharm gets a bit confused on trying to determine the types.

        Args:
            datafile:

        Returns: Count of the number of records loaded.
        """

        # Determine the encoding from the file extension and make sure we can load it.
        supported_types = ["json", "jsonl", "xml", "yaml"]
        encoding = datafile.rsplit(".", 1)[-1]
        if encoding not in supported_types:
            supported_types = ", ".join(f'"{item}"' for item in supported_types)
            raise AttributeError(
                f"""We only understand loading files of types of {supported_types} at the moment, not "{encoding}".""")

        # Load the record data, raising a FileNotFoundError if we cannot find it in our search path.
        for directory in cls.fixture_search_dirs:
            file_path = Path(directory) / datafile
            if file_path.exists() and file_path.is_file():
                with open(file_path, "r") as file:
                    raw_data = file.read()
                break
        else:
            searched = "\n".join("    " + str(path) for path in cls.fixture_search_dirs)
            raise FileNotFoundError(f"""Unable to find "{datafile}". Paths searched were:\n{searched}""")

        # Deserialize the file, given the encoding determined from the file extension.
        objects = serializers.deserialize(encoding, raw_data)

        # Get our model from the first record of the data.
        objects, iter2 = tee(objects)
        trec = next(iter2)
        object_class = trec.object.__class__
        model_class = apps.get_model(object_class.__module__.split(".")[0], object_class.__name__)
        del object_class, trec, iter2

        # Build our set of unsaved records
        records = [
            record.object
            for record in objects
        ]

        # Now do a bulk create of the records
        # noinspection PyUnresolvedReferences
        model_class.objects.bulk_create(records, batch_size=None, ignore_conflicts=False)

        return len(records)

    @classmethod
    def setUpTestData(cls):
        """
        Create our test users and load our test data

        Returns: None
        """

        # noinspection PyUnresolvedReferences
        super().setUpTestData()

        # Set our verbosity value.
        cls.setup_verbosity()

        start = time.perf_counter_ns()

        # Get our user model
        user_model = get_user_model()

        # Save the users as class attributes
        users = user_model.objects.all()
        for index, value in enumerate(users):
            setattr(cls, f"test_user_{index + 1}", value)

        # Load our data for the job applications
        num_records = {}
        for fixture in cls.deferred_fixtures:
            num_records[str(fixture)] = cls.loadFixtureData(fixture)

        end = time.perf_counter_ns()
        if cls.verbosity >= 2:
            print(
                f"Data has been loaded - it took {(end - start) / 1_000_000_000} seconds to load {sum(num_records.values())} from the following files:\n" +
                "\n".join(f"    {fixture} - {cnt} records" for fixture, cnt in num_records.items())
            )

    # noinspection PyUnresolvedReferences
    def setUp(self: SimpleTestCase):
        """
        Create our authenticated client for use by the individual tests.

        Returns: None
        """
        self.client.force_login(self.test_user_1)


class DataTableColumn(NamedTuple):
    data: str
    name: str
    searchable: bool
    orderable: bool
    value: str
    regex: bool


class DataTableTestMixin:
    """
    A mixin providing a number of handy functions for dealing with testing server-side processing of DataTables AJAX
    requesets.
    """
    api_url: str = ""

    columns: list[DataTableColumn] = []

    model = None

    def datatables_query_params(
            self,
            draw: int = 1,
            start: int = 0,
            length: int = 10,
            search: str = None,
            order: list[SortingCriteria] | None = None
    ) -> dict:
        """
        Take self.columns and the named keyword arguments and convert them into the full query parameters for a
        DataTable server-side query.

        https://datatables.net/manual/server-side

        Args:
            draw:
            start:
            length:
            search:
            order:

        Returns: A dictionary usable as the query parameters of a client request
        """

        columns = {
            f"columns[{idx}][{label}]": f"{value}" if label in ["data", "name", "value"] else value
            for idx, (data, name, searchable, orderable, value, regex) in enumerate(self.columns)
            for label, value in zip(["data", "name", "searchable", "orderable", "value", "regex"],
                                    (data, name, searchable, orderable, value, regex))
        }

        if not search:
            search = {
                "search[value]": "",
                "search[regex]": False
            }
        else:
            search = {
                "search[value]": search,
                "search[regex]": False
            }

        if not order:
            order = [
                SortingCriteria(1, "desc", "id"),
                SortingCriteria(2, "asc", "when")
            ]
        order = {
            f"order[{idx}][{label}]": f"{val}"
            for idx, (col, ascdesc, name) in enumerate(order)
            for label, val in zip(["column", "dir", "name"], (col, ascdesc, name))
        }

        return {
            "draw": draw,
            **columns,
            **order,
            "start": start,
            "length": length,
            **search,
        }

    def get_expected_data(
            self,
            user: AbstractBaseUser,
            draw: int = 0,
            start: int = 0,
            length: int = 10,
            filter_func: Callable[[QuerySet], QuerySet] | None = None,
            order_by: list[str] = None
    ) -> dict[str, str | int | dict]:
        """
        A helper method which gets the data we expect to get back on a server-side DataTables AJAX request.

        Args:
            user: The user instance which is being used for the connection.
            draw:
            start:
            length:
            filter_func:
            order_by:

        Returns: A dictionary
        """

        # By default, we sort on the "when" attribute of the application
        if not order_by:
            order_by = ("-id", "-when")

        # Get the records for just the user, filtered by any additional filters which might have been specified.
        user_recs = self.model.objects.all().filter(user_id=user.id)
        records_total = len(user_recs)

        # Apply our filter, if we have one, otherwise just pass the records along.
        if filter_func:
            filtered_recs = filter_func(user_recs)
        else:
            filtered_recs = user_recs
        records_filtered = len(filtered_recs)

        # Now sort them according to our sort criteria.
        sorted_recs = filtered_recs.order_by(*order_by)

        # Now use list comprehension to build the filtered records, only processing the slice we are interested in.
        # noinspection PyUnresolvedReferences
        sorted_recs = [
            self.transform_record_into_dict(record)
            for record in sorted_recs[start:start + length]
        ]

        # Return the results.
        return {
            "status": "success",
            "draw": draw,
            "recordsTotal": records_total,
            "recordsFiltered": records_filtered,
            "job_applications": sorted_recs
        }

    def get_test_arrangement(
            self,
            user: AbstractBaseUser,
            draw: int = 0,
            start: int = 0,
            length: int = 10,
            filter_func: Callable[[QuerySet], QuerySet] | None = None,
            order: list[SortingCriteria] = None,
            order_by: list[str] = None,
            search: str = None
    ) -> tuple[DjangoClient, dict, str]:
        """
        Get the items needed to arrange to make a test request of a DataTables server-side processing method.

        Args:
            user:
            draw:
            start:
            length:
            filter_func:
            order:
            order_by:
            search:

        Returns:
        """

        # noinspection PyUnresolvedReferences
        client = self.client_class()
        client.force_login(user)

        query_data = self.datatables_query_params(
            draw=draw,
            start=start,
            length=length,
            search=search,
            order=order,
        )

        expected_data = self.get_expected_data(
            user=user,
            draw=draw,
            start=start,
            length=length,
            filter_func=filter_func,
            order_by=order_by
        )

        test_url = reverse(self.api_url, query=query_data)

        return (
            client,
            expected_data,
            test_url
        )
