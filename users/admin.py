"""
Our admin interface, which allows for managing users through the Admin side of things.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(AuthUserAdmin):
    """
    Our user administration class, which extends django.contrib.auth.admin.UserAdmin.
    """
