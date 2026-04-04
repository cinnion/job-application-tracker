from django.forms import ModelForm

from . import models


class ProfileForm(ModelForm):
    class Meta:
        model = models.User
        exclude = [
            "id",
            "date_joined",
            "groups",
            "is_active",
            "is_staff",
            "is_superuser",
            "last_login",
            "password",
            "user_permissions",
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
