"""
Our user related forms
"""
from django.forms import ModelForm

from . import models


class ProfileForm(ModelForm):
    """
    The form for a user to be able to edit their profile.
    """

    class Meta:
        """
        Our class metadata, defining the model to use and what fields to exclude from the form.
        """
        model = models.User

        fields = [
            "username",
            "prefix",
            "first_name",
            "middle_name",
            "last_name",
            "suffix",
            "email",
        ]

    field_order = [
        "username",
        "prefix",
        "first_name",
        "middle_name",
        "last_name",
        "suffix",
        "email_address",
    ]
