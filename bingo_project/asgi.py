
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import cards.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(URLRouter(cards.routing.websocket_urlpatterns)),
})
