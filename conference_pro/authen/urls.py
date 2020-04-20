from django.urls import path
from .views import Ping, Register, CheckToken, login, SetPeerId, ConnectToMachine

urlpatterns = [
    path('ping/', Ping.as_view()),
    path('login/', login),
    path('register/', Register.as_view()),
    path('checktoken/', CheckToken.as_view()),
    path('set_peer_id/', SetPeerId.as_view()),
    path('connect_to_machine/', ConnectToMachine.as_view()),
]
