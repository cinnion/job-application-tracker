"""
Signal handlers for signals associated with users.
"""
import logging

from django.contrib.auth.models import Group

# Initialize our logger
logger = logging.getLogger(__name__)


class UserSignalHandlers:  # pylint: disable=too-few-public-methods
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
            logger.info("Added %s to users group.", user.username)
        except Group.DoesNotExist:
            # Handle cases where the group does not exist
            logger.error("Unable to add %s to class users: group does not exist.", user.username)
