import random

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes, api_view

from .consumers import PeersConsumer
from .models import User_settings
from .serializers import UserSerializer, TokenSerializer
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings


@permission_classes([])
class Ping(APIView):
    def get(self, request):
        return Response(status=status.HTTP_200_OK, data="Codeforces orange")


@permission_classes([IsAuthenticated])
class CheckToken(APIView):
    def post(self, request):
        data = User_settings.objects.get(user=request.user).to_dict()
        data['username'] = request.user.username
        return Response(status=status.HTTP_200_OK, data=data)


@permission_classes([IsAuthenticated])
class SetPeerId(APIView):
    def post(self, request):
        user = request.user
        user_settings = User_settings.objects.get(user=user)
        user_settings.peer_id = request.data.get('peer_id', '')
        user_settings.save()
        return Response(status=status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
class ConnectToMachine(APIView):
    def post(self, request):
        user = request.user
        machine_id = request.data['machine_id']
        machine_settings = User_settings.objects.get(user_id=machine_id)
        data = {
            'peer_id': machine_settings.peer_id
        }
        return Response(data=data, status=status.HTTP_200_OK)


@permission_classes([])
class ConnectMachineToMe(APIView):
    def post(self, request):
        print(request.data)
        # user = request.user
        peer_id = request.data['peer_id']
        machine_id = request.data['machine_id']
        return Response(status=status.HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    username = request.data.get("email")
    password = request.data.get("password")
    if username is None or password is None:
        return Response({'error': 'Please provide both username and password'}, status=status.HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_404_NOT_FOUND)
    user_settings = User_settings.objects.get(user=user)
    if user_settings.is_machine:
        user_settings.machine_password = random.randint(1000, 9999)
    user_settings.save()
    token, _ = Token.objects.get_or_create(user=user)
    data = user_settings.to_dict()
    data['username'] = user.username
    data['token'] = token.key
    return Response(data=data, status=status.HTTP_200_OK)

@permission_classes([])
class Register(APIView):
    def post(self, request):
        password = request.data.get("password")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        email = request.data.get("email")
        is_machine = request.data.get("is_machine", False)
        print(type(is_machine))
        username = email
        print(email)
        if username is None or username == "":
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Email is not provided")
        if password is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="password is not provided")
        if first_name is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="first_name is not provided")
        if last_name is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="last_name is not provided")
        check = User.objects.filter(username=username)
        if len(check) > 0:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="username exists")
        user = User.objects.create_user(username, email, password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        user.refresh_from_db()
        user_settings = User_settings(user=user, is_machine=is_machine)

        if is_machine:
            user_settings.machine_password = random.randint(1000, 9999)
        user_settings.save()
        token = TokenSerializer(Token.objects.get(user=user))
        data = user_settings.to_dict()
        data['username'] = user.username
        print(token.data['key'])
        data['token'] = token.data['key']

        return Response(status=status.HTTP_200_OK, data=data)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
