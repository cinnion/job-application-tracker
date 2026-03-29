from django.contrib.auth.views import (
    PasswordChangeView as AuthPasswordChangeView
)
from django.contrib.auth.mixins import PermissionRequiredMixin


class PasswordChangeView(PermissionRequiredMixin, AuthPasswordChangeView):
    """
    Extend the PasswordChangeView from django.contrib.auth to require the change_user_password permission
    from our extended model.
    """
    permission_required = ('users.can_change_password')
