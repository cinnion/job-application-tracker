"""
An extended User model, which adds additional fields for our user, and also implements
a permission to prevent a user (primarily our demo user) from changing their password.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    An extended User model, which adds additional fields for our user, as well as adding a
    new permission, change_user_password, which is required to be able to change the password.
    """

    class Meta:
        """
        Our class metadata, including the table comment and the new permission.
        """
        db_table_comment = "The users for the site"
        permissions = [
            ("change_user_password", "Can change their user password"),
        ]

    prefix = models.CharField(
        _("prefix"),
        max_length=16,
        blank=True,
        help_text=_("The user's name prefix, if any. 16 characters or less"),
        db_comment="The user's name prefix, if any.",
    )
    middle_name = models.CharField(
        _("middle name"),
        max_length=150,
        blank=True,
        help_text=_("User's middle name. Optional, 150 characters or less"),
        db_comment="The user's middle name",
    )
    suffix = models.CharField(
        _("suffix"),
        max_length=16,
        blank=True,
        help_text=_("The user's name suffix, if any. 16 characters or less"),
        db_comment="The user's name suffix, if any.",
    )

    def get_full_name(self):
        if self.middle_name and len(self.middle_name) == 1:
            data = [self.prefix, self.first_name, self.middle_name + ".", self.last_name, self.suffix]
        else:
            data = [self.prefix, self.first_name, self.middle_name, self.last_name, self.suffix]
        return " ".join(filter(None, data))
