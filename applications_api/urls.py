"""
The URLs for dealing with job applications, from the API side of things.
"""
from typing import List, Union

from django.urls import path, URLResolver, URLPattern

from applications_api.views import JobApplications, JobApplicationDetail

app_name = "applications-api"

urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path("", JobApplications.as_view(), name="applications-list"),
    path("<int:pk>", JobApplicationDetail.as_view(), name="application-details")
]
