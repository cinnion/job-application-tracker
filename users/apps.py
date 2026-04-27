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
        from allauth.account.signals import user_signed_up
        from users.signals import UserSignalHandlers
        from .models import User

        user_signed_up.connect(
            UserSignalHandlers.add_user_to_user_group,
            sender=User
        )
