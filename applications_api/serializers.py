"""
The serializer to be used by DRF for job applications.
"""
from rest_framework import serializers

from applications.models import JobApplication


class JobApplicationSerializer(serializers.ModelSerializer):
    """
    The serializer for job applications for use by DRF.
    """

    class Meta:
        """
        The metadata, defining the model and fields for the serializer.
        """
        model = JobApplication
        fields = "__all__"
