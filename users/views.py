"""
Our overridden user views.
"""
import logging
from typing import Any, cast

from allauth.account.utils import url_str_to_user_pk
from allauth.account.views import (
    PasswordChangeView as AllauthPasswordChangeView,
    PasswordResetFromKeyView as AllauthPasswordResetFromKeyView,
)
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from core.views.mixins import Log404Mixin
from .forms import ProfileForm
from .models import User

# Initialize our logger
logger = logging.getLogger(__name__)


class PasswordChangeView(PermissionRequiredMixin, AllauthPasswordChangeView):
    """
    Extend the PasswordChangeView from allauth.account.views to require the change_user_password permission
    from our extended model.
    """
    http_method_names = ["get", "post"]
    permission_required = "users.change_user_password"


class PasswordResetFromKeyView(AllauthPasswordResetFromKeyView):
    """
    Extend the PasswordResetFromKeyView from allauth.account.views to intercept attempts to change the password on
    accounts lacking the 'users.change_user_password' permission. This needs to be done on both the GET and POST actions
    directly, as opposed to through a required permission, as this view is used by anonymous users, rather than
    authenticated users, and we need to look at the target user instead.
    """
    permission_to_check = "users.change_user_password"

    def check_user_permitted(self, request: HttpRequest, uidb36: str) -> None:
        """
        Check to see if the user specified in the reset token is permitted to
        change their password, and do the actual raising of the
        PermissionDenied exception if they are not.

        Args:
            uidb36: The base-36 encoded UID from the reset token.

        Returns: None

        Raises: PermissionDenied exception if the user is denied permission to
        change their password.

        """
        uid = url_str_to_user_pk(uidb36)
        user = cast(User, get_user_model().objects.get(id=uid))
        if not user.has_perm(self.permission_to_check):
            logger.error("Someone at [%s] attempted to do a %s to reset the password for \"%s\" (uid=%d)",
                         request.headers.get("X-Forwarded-For"),
                         request.method,
                         user.username,
                         user.pk
                         )
            raise PermissionDenied(f"User {user.username} is not allowed to change its password")

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Look at the uidb36 value and determine if we should raise a PermissionDenied exception or continue with
        processing.

        Args:
            request: The HttpRequest object.
            *args: A list of positional arguments.
            **kwargs: A list of keyword arguments.

        Returns:
            A response containing ResetPasswordForm.

        Raises:
            PermissionDenied if it is determined that the target of the password reset does not have permission to
            change their password.
        """
        self.check_user_permitted(request, args[0])
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Look at the uidb36 value and determine if we should raise a PermissionDenied exception or continue with
        processing.

        Args:
            request: The HttpRequest object.
            *args: A list of positional arguments.
            **kwargs: A list of keyword arguments.

        Returns:
            A response redirecting to account_reset_password_from_key_done.

        Raises:
            PermissionDenied if it is determined that the target of the password reset does not have permission to
            change their password.
        """
        self.check_user_permitted(request, args[0])
        return super().post(request, *args, **kwargs)

    def put(self, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Look at the uidb36 value and determine if we should raise a PermissionDenied exception or continue with
        processing. This method has the uidb36 offset by 1 from the other methods because of an oddity in how
        the put() method is declared in ProcessFormView.

        Args:
            *args: A list of positional arguments.
            **kwargs: A list of keyword arguments.

        Returns:
            A response redirecting to account_reset_password_from_key_done.

        Raises:
            PermissionDenied if it is determined that the target of the password reset does not have permission to
            change their password.
        """
        self.check_user_permitted(args[0], args[1])
        return super().put(*args, **kwargs)


class EditProfileView(LoginRequiredMixin, Log404Mixin, UpdateView):
    """
    Return the Edit Profile form.

    There is no need to protect against malicious attempts to inject fields like is_staff, is_superuser or to change
    the password, since the ProfileForm extends ModelForm and specifically excludes those fields, which prevents them
    from making it to the clean data. This is why we use frameworks rather than roll our own!
    """
    http_method_names = ["get", "post"]
    model = User
    form_class = ProfileForm
    template_name = "registration/edit_profile.html"
    success_url = reverse_lazy("home")

    def get_object(self, queryset=None):
        return self.request.user
