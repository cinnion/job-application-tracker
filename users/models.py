from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Meta:
        db_table_comment = "The users for the site"

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

    lock_password = models.BooleanField(
        _("lock password"),
        default=False,
        help_text=_("Designates whether the user's password is locked and cannot be change."),
        db_comment="Prevent changing the password if this is True",
    )

    @property
    def is_password_locked(self):
        if self.lock_password is True:
            return True

        return False

    def get_full_name(self):
        data = [self.prefix, self.first_name, self.middle_name, self.last_name, self.suffix]
        return " ".join(filter(None, data))
