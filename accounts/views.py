from rest_framework import status
from rest_framework.views import APIView
from .serializers import (
    LoginUserSerializer, CreateUserSerializer
)
from .models import User
from django.db.models import Count
from django.db.models.functions import TruncMonth
from datetime import datetime
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes


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
                response_data,
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_status(request):
    user = request.user
    status = 'suspended' if not user.is_active else 'active'
    return Response(
        {
            'status': status,
            'role': user.role
        }
    )


class UserStatsView(APIView):
    """
    API endpoint to provide user statistics for the admin dashboard
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        inactive_users = User.objects.filter(is_active=False).count()
        admin_users = User.objects.filter(role='admin').count()
        regular_users = User.objects.filter(role='user').count()

        current_year = datetime.now().year
        user_growth_by_month = [0] * 12

        users_by_month = User.objects.filter(
            date_joined__year=current_year
        ).annotate(
            month=TruncMonth('date_joined')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')

        for entry in users_by_month:
            month_idx = entry['month'].month - 1
            user_growth_by_month[month_idx] = entry['count']

        recent_active_users = User.objects.filter(
            last_login__gte=datetime.now().replace(day=1)
        ).count()
        user_activity_score = int(
            (recent_active_users / active_users) * 100
        ) if active_users > 0 else 0

        return Response({
            'totalUsers': total_users,
            'activeUsers': active_users,
            'inactiveUsers': inactive_users,
            'adminUsers': admin_users,
            'regularUsers': regular_users,
            'userGrowthByMonth': user_growth_by_month,
            'userActivityScore': user_activity_score
        })
