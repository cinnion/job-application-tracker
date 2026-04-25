"""
The URLs for dealing with user management and authentication, including login/logout, password
change/reset, profile editing, etc.
"""
from typing import List, Union

from allauth.account import views as AllauthViews
from django.urls import path, URLResolver, URLPattern

from . import views

urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path("confirm-email/", views.email_verification_sent, name="account_email_verification_sent"),
    path("confirm-email/<key>/", views.ConfirmEmailView.as_view(), name="account_confirm_email"),
    path("email/", AllauthViews.EmailView.as_view(), name="account_email"),
    path("inactive/", AllauthViews.AccountInactiveView.as_view(), name="account_inactive"),
    path("login/", AllauthViews.LoginView.as_view(), name="account_login"),
    path("login/code/confirm/", AllauthViews.ConfirmLoginCodeView.as_view(), name="account_confirm_login_code"),
    path("logout/", AllauthViews.LogoutView.as_view(), name="account_logout"),
    path("password/change/", views.PasswordChangeView.as_view(), name="account_change_password"),
    path("password/reset/", AllauthViews.PasswordResetView.as_view(), name="account_reset_password"),
    path("password/reset/done/", AllauthViews.PasswordResetDoneView.as_view(), name="account_reset_password_done"),
    path("password/reset/key/<uidb36>-<key>/", AllauthViews.PasswordResetFromKeyView.as_view(), name="account_reset_password_from_key"),
    path("password/reset/key/done/", AllauthViews.PasswordResetFromKeyDoneView.as_view(), name="account_reset_password_from_key_done"),
    path("password/set/", AllauthViews.PasswordSetView.as_view(), name="account_set_password"),
    path("reauthenticate/", AllauthViews.ReauthenticateView.as_view(), name="account_reauthenticate"),
    path("signup/", AllauthViews.SignupView.as_view(), name="account_signup"),
    path("profile/edit/", views.EditProfileView.as_view(), name="profile")
]
