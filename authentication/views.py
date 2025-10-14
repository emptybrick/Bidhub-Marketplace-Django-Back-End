from rest_framework.views import APIView # main API controller class
from rest_framework.response import Response #response class, like res object in express
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from datetime import datetime, timedelta # creates timestamps in dif formats
from django.contrib.auth import get_user_model # gets user model we are using
from django.conf import settings # import our settings for our secret
from .serializers import UserSerializer
import jwt # import jwt

User = get_user_model() # Save user model to User var

class RegisterView(APIView):

    def post(self, request):
        user_to_create = UserSerializer(data=request.data)
        print('USER CREATE', user_to_create)
        if user_to_create.is_valid():
            user_to_create.save()
            return Response({'message': 'Registration successful'}, status=status.HTTP_202_ACCEPTED)
        return Response(user_to_create.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

class LoginView(APIView):

    def post(self, request):
        # get data from the request
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user_to_login = User.objects.get(email=email) # get user with email
        except User.DoesNotExist:
            raise PermissionDenied(detail='Invalid Credentials') # throw error
        if not user_to_login.check_password(password):
            raise PermissionDenied(detail='Invalid Credentials')

        # timedelta can be used to calculate the difference between dates - passing 7 days gives you 7 days represented as a date that we can add to datetime.now() to get the date 7 days from now
        dt = datetime.now() + timedelta(days=7) # validity of token
        token = jwt.encode(
            {'sub': str(user_to_login.id), 'exp': int(dt.strftime('%s'))}, # strftime -> string from time and turning it into a number
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        return Response({ 'token': token, 'message': f"Welcome back {user_to_login.username}"})