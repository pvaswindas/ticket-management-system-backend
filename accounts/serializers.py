from .models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from .validators import validate_password
from django.core.validators import validate_email


class LoginUserSerializer(serializers.Serializer):
    """Serializer for validating a user data to login."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.CharField(required=False)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError(
                "Both email and password are required."
            )

        email = email.lower().strip()

        try:
            user = User.objects.get(email=email)

            if not user.is_active:
                raise serializers.ValidationError(
                    "Account has been suspended."
                )

            authenticated_user = authenticate(
                request=self.context.get('request'),
                email=email,
                password=password
            )

            if not authenticated_user:
                raise serializers.ValidationError(
                    "Incorrect password. Please try again."
                )

            attrs['user'] = authenticated_user
            return attrs

        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")


class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer for creating a user with strong password validation."""

    confirm_password = serializers.CharField(write_only=True)
    role = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = [
            'email',
            'password',
            'confirm_password',
            'role',
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_email(self, value):
        """Ensure email is valid and unique"""
        validate_email(value)
        value = value.lower().strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        return value

    def validate_password(self, value):
        """Ensure password is strong."""
        return validate_password(value)

    def validate(self, data):
        """Ensure password and confirm_password match."""
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError(
                {
                    "confirm_password": "Passwords do not match."
                }
            )
        return data

    def create(self, validated_data):
        """Create a user or superuser based on role."""
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        role = validated_data.pop('role', 'user').lower().strip()

        if role == "admin":
            return User.objects.create_superuser(
                email=validated_data['email'], password=password
            )
        return User.objects.create_user(
            email=validated_data['email'], password=password
        )
