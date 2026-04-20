"""
The URLs for dealing with user management and authentication, including login/logout, password
change/reset, profile editing, etc.
"""
from typing import List, Union

from django.contrib.auth import views as AdminViews
from django.urls import path, URLResolver, URLPattern
from . import views

urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path("login/", AdminViews.LoginView.as_view(), name="account_login"),
    path("logout/", AdminViews.LogoutView.as_view(), name="account_logout"),
    path("password_change/", views.PasswordChangeView.as_view(), name="account_change_password"),
    path("password_change/done/", AdminViews.PasswordChangeDoneView.as_view(), name="password_change_done"),
    path("password_reset/", AdminViews.PasswordResetView.as_view(), name="account_reset_password"),
    path("password_reset/done/", AdminViews.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", AdminViews.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", AdminViews.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path("profile/edit/", views.EditProfileView.as_view(), name="profile")
]
