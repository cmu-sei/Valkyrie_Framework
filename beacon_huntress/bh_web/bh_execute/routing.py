from django.urls import path, re_path
from bh_web.bh_execute.consumers import NotificationConsumer

# websocket_urlpatterns = [
#     path('ws/notifications/', NotificationConsumer.as_asgi()),
# ]

websocket_urlpatterns = [
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
]