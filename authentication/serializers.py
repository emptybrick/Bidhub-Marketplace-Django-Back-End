from rest_framework import serializers
# function runs when creating superuser
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.hashers import make_password  # hashes password for us
from django.core.exceptions import ValidationError

User = get_user_model()

# never converted to json and returned in response


class UserSerializer(serializers.ModelSerializer):
    # write_only=True ensures never sent back in JSON
    password = serializers.CharField(write_only=True)
    password_confirmation = serializers.CharField(write_only=True)

    def validate(self, data):  # data comes from the request body
        # Only validate password if both password and password_confirmation are provided
        if 'password' in data and 'password_confirmation' in data:
            password = data.pop('password')
            password_confirmation = data.pop('password_confirmation')

            # Check if passwords match
            if password != password_confirmation:
                raise ValidationError(
                    {'password_confirmation': 'Passwords do not match'})

            # Validate password strength
            try:
                password_validation.validate_password(password=password)
            except ValidationError as err:
                raise ValidationError({'password': err.messages})

            # Hash the password
            data['password'] = make_password(password)
        elif 'password' in data or 'password_confirmation' in data:
            # If only one of password or password_confirmation is provided, raise an error
            raise ValidationError(
                {'password_confirmation': 'Both password and password_confirmation are required'})
        return data

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'user_rating', 'favorites',
            'password', 'password_confirmation', 'items_sold', "date_joined", 'profile_image'
        )        

class UsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username',)
        read_only_fields = ('id', 'username')

class SellerProfileViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'user_rating', 'items_sold', "date_joined", "profile_image")
        read_only_fields = ('id', 'username', 'user_rating',
                            'items_sold', "date_joined", "profile_image")
