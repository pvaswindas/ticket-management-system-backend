from rest_framework import status
from rest_framework.views import APIView
from .serializers import (
    LoginUserSerializer, CreateUserSerializer
)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAdminUser


class RegisterUserView(APIView):
    """API endpoint for user registration."""

    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "User created successfully!",
                    "email": user.email,
                    "role": user.role
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    API View for user login that returns JWT tokens
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginUserSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            user = serializer.validated_data['user']

            refresh = RefreshToken.for_user(user)

            response_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                "email": user.email,
                "role": user.role
            }

            return Response(
                {
                    'status': 'success',
                    'data': response_data,
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                'status': 'error',
                'message': 'Validation failed. Please check your input.',
                'error': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class LogoutView(APIView):
    """
    API View for user logout that blacklists the refresh token
    """
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')

            if not refresh_token:
                return Response(
                    {
                        'status': 'error',
                        'message': 'Refresh token is required'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {
                    'status': 'success',
                    'message': 'Logout successful'
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {
                    'status': 'error',
                    'message': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
