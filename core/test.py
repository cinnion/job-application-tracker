"""
This class provides a common set of extended base classes for our class based unit/function
tests, combining the main test classes from django.test with ParameterizedTestCase, so that
we can create parameterized tests without having to explicitly include that class over and
over. In addition, we create an extended Client class which injects the headers we expect
to see in every request due to the application running behind a proxy.
"""
from django import test
from django.test.client import (
    Client as DjangoClient,
    RequestFactory,
)
from unittest_parametrize import ParametrizedTestCase


class Client(DjangoClient, RequestFactory):
    """
    An extended version of django.test.client.Client which injects the headers
    we expect to see from being behind a proxy into every request.
    """

    def __init__(self,
                 enforce_csrf_checks: bool = False,
                 raise_request_exception: bool = True,
                 *,
                 headers: dict = None,
                 query_params: dict = None,
                 **defaults,
                 ) -> None:
        """
        Our overridden client class, which allows us to inject our headers into
        the default client instance.

        Args:
            enforce_csrf_checks: Whether we are to enforce our CSRF checks.
            raise_request_exception: Whether we raise any exception raised
                                    during the request handling.
            headers: Any headers we are to have for the request.
            query_params: Any query parameters we are to have.
            **defaults: Defaults
        """
        my_headers = {
            "X-Forwarded-For": "192.168.8.194, 10.0.0.2",
            "X-Forwarded-Port": "443",
            "X-Forwarded-Host": "testserver",
            "X-Forwarded-Proto": "http",
            "X-Forwarded-Server": "testserver",
            "X-Real-IP": "10.0.0.2",
        }
        if headers:
            headers = my_headers | headers
        else:
            headers = my_headers
        super().__init__(enforce_csrf_checks=enforce_csrf_checks,
                         raise_request_exception=raise_request_exception,
                         headers=headers,
                         query_params=query_params,
                         **defaults
                         )


class SimpleTestCase(ParametrizedTestCase, test.SimpleTestCase):
    """
    An extended version of django.test.SimpleTestCase, which includes ParameterizedTestCase
    for us already.
    """
    client_class = Client


class TestCase(SimpleTestCase, test.TestCase):
    """
    An extended version of django.test.TestCase, which includes ParameterizedTestCase for us
    already.
    """


class TransactionTestCase(SimpleTestCase, test.TransactionTestCase):
    """
    And extended version of django.test.TransactionTestCase, which includes ParameterizedTestCase
    for us already.
    """


class LiveServerTestCase(SimpleTestCase, test.LiveServerTestCase):
    """
    An extended version of django.test.LiveServerTestCase, which includes ParameterizedTestCase
    for us already.
    """
