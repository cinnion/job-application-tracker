import unittest

from allauth.account.signals import user_signed_up
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.http.request import HttpRequest

from core.test import TestCase


class TestUserSignalHandler(TestCase):
    def test_user_created_but_group_does_not_exist(self):
        # Arrange
        data = {
            "username": "testuser",
            "password": "Yfr_A0Qdk7W-s2s01Mec ",
            "email": "testuser@example.com"
        }
        user = get_user_model().objects.create(**data)
        request = HttpRequest()
        signal_kwargs = {}

        # Act/Assert
        with self.assertLogs('users.signals', level='INFO') as cm:
            user_signed_up.send(sender=user.__class__, request=request, user=user, **signal_kwargs)
            self.assertIn("ERROR:users.signals:Unable to add testuser to class users: group does not exist.", cm.output[0])

    def test_user_created_and_group_exists_added_to_group(self):
        # Arrange
        call_command("loaddata", "core/tests/fixtures/users.json", verbosity=0)
        data = {
            "username": "testuser",
            "password": "Yfr_A0Qdk7W-s2s01Mec ",
            "email": "testuser@example.com"
        }
        user = get_user_model().objects.create(**data)
        request = HttpRequest()
        signal_kwargs = {}

        # Act/Assert
        with self.assertLogs('users.signals', level='INFO') as cm:
            user_signed_up.send(sender=user.__class__, request=request, user=user, **signal_kwargs)
            self.assertIn("INFO:users.signals:Added testuser to users group.", cm.output[0])

        # Assert
        self.assertTrue(user.groups.filter(name="users").exists())


if __name__ == '__main__':
    unittest.main()
