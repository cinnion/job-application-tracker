"""
This class provides a common set of extended base classes for our class based unit/function
tests, combining the main test classes from django.test with ParameterizedTestCase, so that
we can create parameterized tests without having to explicitly include that class over and
over.
"""
from django import test
from unittest_parametrize import ParametrizedTestCase


class SimpleTestCase(ParametrizedTestCase, test.SimpleTestCase):
    """
    An extended version of django.test.SimpleTestCase, which includes ParameterizedTestCase
    for us already.
    """


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
