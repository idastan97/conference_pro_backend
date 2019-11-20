from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes, api_view
from .serializers import UserSerializer
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

@permission_classes([])
class CheckToken(APIView):
    def post(self, request):
        token = request.headers.get("token", '')
        check_token = Token.objects.filter(key=token)
        if len(check_token) == 0:
            return Response(status=status.HTTP_404_NOT_FOUND, data="Token does not exist")
        return Response(status=status.HTTP_200_OK, data="Codeforces orange")

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if username is None or password is None:
        return Response({'error': 'Please provide both username and password'}, status=status.HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key}, status=status.HTTP_200_OK)

@permission_classes([])
class Register(APIView):
    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        if username is None or username == "":
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Username is not provided")
        if password is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="password is not provided")
        if email is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="email is not provided")
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
        userout = UserSerializer(user)
        return Response(status=status.HTTP_200_OK, data=userout.data)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
