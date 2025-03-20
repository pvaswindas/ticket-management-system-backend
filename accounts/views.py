from rest_framework import status
from rest_framework.views import APIView
from .serializers import LoginUserSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny


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
            user_data = UserSerializer(user).data

            response_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': user_data
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
