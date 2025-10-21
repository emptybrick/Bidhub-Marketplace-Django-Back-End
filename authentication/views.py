from rest_framework.views import APIView  # main API controller class
# response class, like res object in express
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from datetime import datetime, timedelta  # creates timestamps in dif formats
from django.contrib.auth import get_user_model  # gets user model we are using
from django.conf import settings  # import our settings for our secret
from .serializers import UserSerializer
from .models import User, BlackListedToken
import jwt  # import jwt
from items.models import Item

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
        # can set to username instead of email here
        email = request.data.get('email') if request.data.get(
            'email') is not None else None
        password = request.data.get('password')

        try:
            user_to_login = User.objects.get(email=email)

        except User.DoesNotExist:
            raise PermissionDenied(detail='Invalid Credentials')

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
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        serialized_user = UserSerializer(request.user)
        return Response(serialized_user.data, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):

        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', "")

            BlackListedToken.objects.create(token=token)

            return Response(
                {"message": "Logout successful!"},
                status=status.HTTP_200_OK
            )

        return Response(
            {"message": "No valid token Found"},
            status=status.HTTP_400_BAD_REQUEST
        )

# GET All Users - Admin Only & Development


class UserListView(APIView):
    #    """View for retrieving user profile information"""
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        """Get all users for testing purposes"""
        # Create base queryset
        users = User.objects.all()

        # Use populated serializer if detailed=true is requested
        serialized_users = UserSerializer(users, many=True)

        return Response(serialized_users.data, status=status.HTTP_200_OK)
    

class ToggleFavoriteView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        item_id = request.data.get('item_id')
        
        # Validate item_id
        if not item_id:
            return Response(
                {'error': 'item_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        item = Item.objects.get(pk=str(item_id))
        if item.owner == request.user:
            return Response(
                {'error': 'Can not favorite your own item.'},
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
        try:
            # Ensure item_id is string/int as needed
            item_id = str(item_id)
            request.user.toggle_favorite(item_id)

            return Response({
                'success': True,
                'is_favorited': request.user.is_favorited(item_id),
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class FavoritesListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({
            'favorites': request.user.favorites or [],
        }, status=status.HTTP_200_OK)

# GET Single User Profile




            # # PUT Update User Profile
            # class ProfileUpdateView(APIView):
            #     permission_classes = (IsAuthenticated,)

            #     def put(self, request):
            #         user = request.user
            #         serializer = UserSerializer(user, data=request.data, partial=True)
            #         if serializer.is_valid():
            #             serializer.save()
            #             return Response(serializer.data)
            #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
