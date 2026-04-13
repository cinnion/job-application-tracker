"""
The utility functions used for this project, mainly by the context processors.
"""
import json
import os

from django.conf import settings


def get_build_info():
    """
    Get the build information from the build_info.json file, returning an error if the
    file is not found or could not be decoded, along with an array of N/A values.

    Returns:
        A dictionary of information about the build.

    """
    build_info_path = os.path.join(settings.BASE_DIR, "build_info.json")
    error = None

    try:
        with open(build_info_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        error = "The file 'build_info.json' was not found."
    except json.JSONDecodeError:
        error = "Could not decode JSON from the file build_info.json."

    return {
        "Error": error,
        "BUILD_NUMBER": "N/A",
        "BUILD_ID": "N/A",
        "JOB_NAME": "N/A",
        "BUILD_URL": "N/A",
        "GIT_COMMIT": "N/A",
        "GIT_BRANCH": "N/A",
        "BUILD_DATE": "N/A",
    }
