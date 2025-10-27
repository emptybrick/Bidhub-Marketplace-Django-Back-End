from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.conf import settings  # show secret key in settings.py
import jwt
from .models import BlackListedToken

User = get_user_model()

# BasicAuthentication has stuff built in like password & email validation


# assertain users permissions # requests come through here # assign a permission level # if valid token -> given permission to see secure things
class JWTAuthentication(BasicAuthentication):
    def authenticate(self, request):  # check request has token and return if so
        header = request.headers.get('Authorization')

        # if no headers, just return to end the request
        if not header:
            return None

        # if token is wrong format, throw error
        if not header.startswith('Bearer'):
            raise PermissionDenied(detail='Invalid Auth token')

        # pass all checks, store token in variable
        token = header.replace('Bearer ', '')

        # check for BlackListedToken
        try:
            BlackListedToken.objects.get(token=token)
            raise PermissionDenied(detail='Token has been revoked')
        except BlackListedToken.DoesNotExist:
            pass

        # get payload with users id from token & algorithms
        try:
            # can show https://jwt.io again so they can see the alg and the secret
            # HS256 is default, it will be this unless we specify a different alg when we sign the token
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=['HS256'])

            # find user with that id in db
            user = User.objects.get(pk=payload.get('sub'))
            # issue with the token

        # if we get an error when decoding it will fall into the below exception
        except jwt.exceptions.InvalidTokenError:
            raise PermissionDenied(detail='Invalid Token')

        # If the user does not exist it will fall into the below
        except User.DoesNotExist:
            raise PermissionDenied(detail='User Not Found')

        # if all good, return user and the token
        return (user, token)
