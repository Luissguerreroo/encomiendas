import os
import django

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

# ─────────────────────────────
# Django setup
# ─────────────────────────────
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# IMPORTANTE:
# Estos imports deben ir DESPUÉS de django.setup()
from channels_middleware import JWTAuthMiddlewareStack
from envios.routing import websocket_urlpatterns


# ─────────────────────────────
# ASGI APPLICATION
# ─────────────────────────────
application = ProtocolTypeRouter({

    # HTTP normal
    "http": get_asgi_application(),

    # WebSockets
    
    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    ),
})