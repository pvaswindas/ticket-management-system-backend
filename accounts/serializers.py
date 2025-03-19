from .models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.validators import validate_email


class UserSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'is_active']


class LoginUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            email = email.lower().strip()

            try:
                user = User.objects.get(email=email)

                if not user.is_active:
                    raise serializers.ValidationError(
                        "Account has been suspended"
                    )

                # Authenticate user
                authenticated_user = authenticate(
                    request=self.context.get('request'),
                    email=email,
                    password=password
                )

                if not authenticated_user:
                    raise serializers.ValidationError(
                        "Invalid email or password"
                    )

                attrs['user'] = authenticated_user
                return attrs
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid email or password")

        raise serializers.ValidationError("")


class CreateUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
