from django.conf.urls import url
from competitors.consumers import RS232Consumer

websocket_urlpatterns = [
    url(r'^ws/rs232/(?P<room_code>\w+)/$', RS232Consumer.as_asgi()),
]