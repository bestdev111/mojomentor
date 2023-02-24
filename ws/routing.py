from django.urls import path
from .consumers import MyAsyncConsumer


websocket_urlpatterns = [
    path('ws/chat', MyAsyncConsumer.as_asgi()),
]
