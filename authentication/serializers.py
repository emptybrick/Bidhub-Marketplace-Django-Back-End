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
        print('DATA', data)
        # remove fields from request body and save to vars
        password = data.pop('password')
        password_confirmation = data.pop('password_confirmation')

        # check if they match
        if password != password_confirmation:
            raise ValidationError({'password_confirmation': 'do not match'})

        # checks if password is valid, review this out so it works
        try:
            password_validation.validate_password(password=password)
        except ValidationError as err:
            print('VALIDATION ERROR')
            raise ValidationError({'password': err.messages})

        # hash the password, reassigning value on dict
        data['password'] = make_password(password)

        print('DATA ->', data)
        return data

    class Meta:
        model = User
        # We explicitly define fields rather than using fields="__all__" to control exactly what user data is exposed
        # This prevents accidentally exposing sensitive fields like password hash or security questions
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'password', 'password_confirmation',
                  'street_address', 'city', 'state', 'postal_code', 'country', 'phone_number', 'wallet', 'user_rating')
