import re
from rest_framework import serializers


def validate_password(password):
    """
    Validates that the password is strong enough.
    """
    if len(password) < 8:
        raise serializers.ValidationError(
            "Password must be at least 8 characters long"
        )
    if not re.search(r'[A-Z]', password):
        raise serializers.ValidationError(
            "Password must contain at least one uppercase letter."
        )
    if not re.search(r'[a-z]', password):
        raise serializers.ValidationError(
            "Password must contain at least one lowercase letter."
        )
    if not re.search(r'\d', password):
        raise serializers.ValidationError(
            "Password must contain at least one digit."
        )
    if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
        raise serializers.ValidationError(
            "Password must contain at least one special character."
        )
    return password
