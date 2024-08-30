from django.contrib.auth import authenticate
from django.contrib.auth.handlers.modwsgi import check_password
from rest_framework import serializers
from .models import UserModel
from rest_framework_simplejwt.tokens import RefreshToken


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('id', 'username', 'password')
        extra_kwargs = {
            'id': {'read_only': True},
            'username': {'required': True},
            'password': {'write_only': True},
        }

    def validate_username(self, value):
        if UserModel.objects.filter(username=value).exists():
            raise serializers.ValidationError('This username is already taken.')
        return value

    def validate(self, data):
        data = super().validate(data)
        return data

    def create(self, validated_data):
        user = UserModel.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=500, write_only=True)

    def validate(self, data):
        username = data.get('username', None)
        password = data.get('password', None)
        if username is None:
            raise serializers.ValidationError('A username is required to log in.')
        if password is None:
            raise serializers.ValidationError('A password is required to log in.')
        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError('A user with this username and password was not found.')
        refresh = RefreshToken.for_user(user)
        return {
            'username': user.username,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
