from django.urls import path
from .views import Ping, Register, CheckToken, login

urlpatterns = [
    path('ping/', Ping.as_view()),
    path('login/', login),
    path('register/', Register.as_view()),
    path('checktoken/', CheckToken.as_view()),
]
