from __future__ import absolute_import, unicode_literals
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bh_web.settings")

# SET APP
app = Celery("bh_execute")

# CONFIGURATION OBJECT TO CHILD PROCESSES & AUTO DISCOVER TASKS
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Manual import of tasks
# import bh_web.bh_execute.tasks


# # Settings
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bh_web.settings")

# # Set APP
# app = Celery("celery")

# # the configuration object to child processes.
# app.config_from_object("django.conf:settings", namespace="CELERY")

# # Auto-discover tasks from installed apps
# app.autodiscover_tasks()


# from celery import Celery

# # Initialize Celery with the broker URL
# app = Celery(
#     'hello',
#     broker='redis://redis:6379/0',
#     backend='redis://redis:6379/0'
# )

# @app.task
# def say_hello(name):
#     return f"Hello, {name}!"

# @app.task
# def example_task(x,y):
#     return x * y