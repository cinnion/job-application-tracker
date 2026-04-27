"""
Signal handlers for signals associated with users.
"""
import logging

from django.contrib.auth.models import Group

# Initialize our logger
logger = logging.getLogger(__name__)


class UserSignalHandlers:
    """
    The signal handlers for signals related to users.
    """

    @staticmethod
    def add_user_to_user_group(request, user, **kwargs) -> None:
        """
        Add the new user to the users group after signing up via allauth.

        Args:
            request: HttpRequest
            user: User
            **kwargs: The keyword arguments.
        Returns:
        """
        try:
            group = Group.objects.get(name="users")
            user.groups.add(group)
            logger.info(f"Added {user.username} to class users.")
        except Group.DoesNotExist:
            # Handle cases where the group does not exist
            logger.error(f"Unable to add {user.username} to class users: group does not exist.")
