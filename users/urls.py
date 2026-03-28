from typing import List, Union

from django.contrib.auth import views as AdminViews
from django.urls import path, URLResolver, URLPattern


urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path("login/", AdminViews.LoginView.as_view(), name="login"),
    path("logout/", AdminViews.LogoutView.as_view(), name="logout"),
    path("password_change/", AdminViews.PasswordChangeView.as_view(), name="password_change"),
    path("password_change/done/", AdminViews.PasswordChangeDoneView.as_view(), name="password_change_done"),
    path("password_reset/", AdminViews.PasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", AdminViews.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", AdminViews.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", AdminViews.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
]
