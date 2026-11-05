import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
from django.core.asgi import get_asgi_application
django_app=get_asgi_application()
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from exchange.routing import websocket_urlpatterns
application=ProtocolTypeRouter({"http":django_app,"websocket":AuthMiddlewareStack(URLRouter(websocket_urlpatterns))})
