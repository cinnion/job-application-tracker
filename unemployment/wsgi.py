"""
WSGI config for unemployment project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import pydevd_pycharm

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unemployment.settings')

pydevd_pycharm.settrace('wing-1.home.ka8zrt.com', port=6767, stdoutToServer=True, stderrToServer=True, suspend=True, trace_only_current_thread=True)

application = get_wsgi_application()
