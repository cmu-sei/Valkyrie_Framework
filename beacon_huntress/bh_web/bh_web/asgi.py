"""
ASGI config for bh_web project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bh_web.settings')

# application = get_asgi_application()

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from starlette.middleware.wsgi import WSGIMiddleware
from starlette.routing import Mount, Router

from bh_execute.routing import websocket_urlpatterns
from bh_api.api import app as fastapi_app

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bh_web.settings')

django_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": Router([
        Mount("/api", app=fastapi_app),
        Mount("/", app=django_app),
    ]),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})