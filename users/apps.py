"""
The configuration for the user app.
"""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Define the name for the application.
    """
    name = 'users'

    def ready(self) -> None:
        """
        Connect our signal handlers here.

        Returns: None
        """
        from allauth.account.signals import user_signed_up  # pylint: disable=import-outside-toplevel
        from users.signals import UserSignalHandlers  # pylint: disable=import-outside-toplevel
        from .models import User  # pylint: disable=import-outside-toplevel

        user_signed_up.connect(
            UserSignalHandlers.add_user_to_user_group,
            sender=User
        )
