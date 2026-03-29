from typing import Dict

from django.conf import settings
from django.http import HttpRequest

from .utils import get_build_info


def build_info_processor(request: HttpRequest) -> Dict[str, Dict[str, str]]:
    """
    Return the build information dictionary as BUILD_INFO.

    :param request: The HTTP request
    :return: The build info dictionary under BUILD_INFO.
    """
    return {"BUILD_INFO": get_build_info()}


def site_name_processor(request: HttpRequest) -> Dict[str, str]:
    """
    Return the site name as SITE_NAME.

    :param request: The HTML request
    :return: The site name in a dictionary under SITE_NAME.
    """
    return {"SITE_NAME": settings.SITE_NAME}
