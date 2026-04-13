"""
Our overridden user views.
"""
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.views import (
    PasswordChangeView as AuthPasswordChangeView
)
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from core.views.mixins import Log404Mixin
from .forms import ProfileForm
from .models import User


class PasswordChangeView(PermissionRequiredMixin, AuthPasswordChangeView):
    """
    Extend the PasswordChangeView from django.contrib.auth to require the change_user_password permission
    from our extended model.
    """
    http_method_names = ["get", "post"]
    permission_required = 'users.change_user_password'


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
