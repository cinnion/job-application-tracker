"""
Allow the Admin interface to be able to work with job applications.
"""
from django.contrib import admin

from .models import JobApplication


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    """
    Model for doing administration of JobApplications
    """
    readonly_fields = ('created_at', 'updated_at')
