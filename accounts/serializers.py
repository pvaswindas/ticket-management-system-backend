from .models import User
from rest_framework import serializers
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'is_active']


class LoginUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.CharField(required=False)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        role = attrs.get('role')

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
                raise serializers.ValidationError("Invalid email or password.")

            if role and authenticated_user.role != role.lower():
                raise serializers.ValidationError(
                    f"User does not have {role} permissions."
                )

            attrs['user'] = authenticated_user
            return attrs

        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")
