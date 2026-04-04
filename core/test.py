from django import test
from unittest_parametrize import ParametrizedTestCase


class SimpleTestCase(ParametrizedTestCase, test.SimpleTestCase):
    pass


class TestCase(SimpleTestCase, test.TestCase):
    pass


class TransactionTestCase(SimpleTestCase, test.TransactionTestCase):
    pass


class LiveServerTestCase(SimpleTestCase, test.LiveServerTestCase):
    pass
