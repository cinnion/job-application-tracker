"""
Our form for a job application, with a class to allow us to have Date fields.
"""
from django import forms
from django.forms import ModelForm

from . import models


class DateInput(forms.DateInput):
    """
    A class for creating input fields of type date.
    """
    input_type = "date"


class EditApplication(ModelForm):
    """
    The form for creating/editing the details associated with a job application.
    """

    class Meta:
        """
        The model, fields to be excluded and widgets to be used for our form.
        """
        model = models.JobApplication
        fields = [
            "when",
            "company",
            "title",
            "posting",
            "confirm",
            "notes",
            "active",
            "interviews",
            "rejected",
        ]

        widgets = {
            "when": DateInput(),
            "rejected": DateInput(),
        }
