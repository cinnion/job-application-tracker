"""
This is a set of mixins for testing the server-side AJAX calls made by a DataTable instance.
"""
from typing import Callable, NamedTuple, TypeVar

from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import Model, QuerySet
from django.test.client import Client as DjangoClient
from django.urls import reverse

# Define a generic type for templating with a database model.
M = TypeVar("M", bound=Model)


# Define a named tuple for sorting criteria
class SortingCriteria(NamedTuple):
    column: int
    ascdesc: str
    name: str


class DataTableColumn(NamedTuple):
    data: str
    name: str
    searchable: bool
    orderable: bool
    value: str
    regex: bool


class DataTableTestMixin:
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
