from django import forms
from django.forms import ModelForm

from . import models


class DateInput(forms.DateInput):
    input_type = "date"


class EditApplication(ModelForm):
    class Meta:
        model = models.JobApplication
        exclude = [
            "id",
            "user",
        ]

        widgets = {
            "when": DateInput(),
            "rejected": DateInput(),
        }
