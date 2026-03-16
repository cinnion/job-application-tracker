import json
import os
from django.conf import settings


def get_build_info():
    build_info_path = os.path.join(settings.BASE_DIR, 'build_info.json')
    try:
        with open(build_info_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        error = "The file 'build_info.json' was not found."
    except json.JSONDecodeError:
        error = 'Could not decode JSON fron the file build_info.json.'

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
