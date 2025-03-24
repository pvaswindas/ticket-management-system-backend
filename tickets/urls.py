from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.TicketViewSet, basename='ticket')

urlpatterns = [
    path(
        'stats/', views.TicketStatsView.as_view(), name='ticket-stats'
    ),
    path(
        'user-stats/',
        views.UserTicketStatsView.as_view(),
        name='user-ticket-stats'
    ),
    path('', include(router.urls)),
]
