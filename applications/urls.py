from typing import List, Union

from django.urls import path, URLResolver, URLPattern
from . import views

app_name = 'applications'

urlpatterns: List[Union[URLResolver, URLPattern]] = [
    path('', views.Applications.as_view(), name='application-list'),
    path("<int:appid>/edit", views.ApplicationDetails.as_view(), name="application-details"),
    path("new-application/", views.ApplicationDetails.as_view(), name="new-application"),
]
