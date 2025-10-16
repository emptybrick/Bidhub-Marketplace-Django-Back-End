from rest_framework.views import APIView  # main API controller class
# response class, like res object in express
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from datetime import datetime, timedelta  # creates timestamps in dif formats
from django.contrib.auth import get_user_model  # gets user model we are using
from django.conf import settings  # import our settings for our secret
from .serializers import UserSerializer
import jwt  # import jwt
from rest_framework.permissions import IsAuthenticated

User = get_user_model()  # Save user model to User var


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
            user_to_login = User.objects.get(
                email=email)  # get user with email
        except User.DoesNotExist:
            raise PermissionDenied(detail='Invalid Credentials')  # throw error
        if not user_to_login.check_password(password):
            raise PermissionDenied(detail='Invalid Credentials')

        # timedelta can be used to calculate the difference between dates - passing 7 days gives you 7 days represented as a date that we can add to datetime.now() to get the date 7 days from now
        dt = datetime.now() + timedelta(days=7)  # validity of token
        token = jwt.encode(
            # strftime -> string from time and turning it into a number
            {'sub': str(user_to_login.id), 'exp': int(dt.strftime('%s'))},
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        return Response({'token': token, 'message': f"Welcome back {user_to_login.username}"})


class UserView(APIView):
    """View for retrieving user profile information"""

    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        # Check if user is requesting their own profile or has admin permissions
        if request.user.id == pk or request.user.is_staff:
            try:
                user = get_user_model().objects.get(pk=pk)
                serializer = UserSerializer(user)
                return Response(serializer.data)
            except get_user_model().DoesNotExist:
                return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(
                {"detail": "You don't have permission to view this profile"},
                status=status.HTTP_403_FORBIDDEN
            )


class ProfileUpdateView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
