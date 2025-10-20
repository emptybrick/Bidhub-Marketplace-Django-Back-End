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
        # We explicitly define fields rather than using fields="__all__" to control exactly what user data is exposed
        # This prevents accidentally exposing sensitive fields like password hash or security questions
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'password', 'password_confirmation',
                  'street_address', 'city', 'state', 'postal_code', 'country', 'phone_number', 'wallet', 'user_rating', 'favorites')
