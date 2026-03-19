import multiprocessing
import os

# The socket to bind
# A string of the form: 'HOST', 'HOST:PORT' or 'unix:PATH'
bind = os.getenv('GUNICORN_BIND', default="0.0.0.0:8000")

# The number of pending connections queue size
backlog = 2048

# Worker processes
# Usually set to 2-4 x $(NUM_CORES)
workers = os.getenv("GUNICORN_WORKERS", default=multiprocessing.cpu_count() * 2 + 1)
workers = 1
# The type of workers to use (sync, gevent, eventlet, etc.)
# worker_class = 'sync'

# Kill and restart workers silent for more than this many seconds (helps with memory leaks)
timeout = 3600

# Logging
# Logging to stdout
accesslog = '-'
errorlog = '-'
loglevel = 'info'  # debug, info, warning, error, critical

# The WSGI application path in pattern $(MODULE_NAME):$(VARIABLE_NAME)
wsgi_app = 'unemployment.wsgi:application'
